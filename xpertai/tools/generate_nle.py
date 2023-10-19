from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import LLMChain, PromptTemplate
from xpertai.prompts import REFINE_PROMPT, FORMAT_LABLES
from .utils import *


def gen_nle(arg_dict):
    '''Takes a dictionary as input in the form:
    {"observation":<target property>,
    "XAI_tool": <SHAP, LIME or Both>,
    "top_k":<maximum number of features to explain>
    }

    Example:
    {"lit_directory:"data/arxiv_downloads",
    "XAI_tool": "SHAP",
    "top_k":5}
    '''

    save_dir = './data'
    # arg_dict = json.loads(json_request)
    for k, val in arg_dict.items():
        globals()[k] = val

    # begin extracting information
    if XAI_tool == "SHAP":
        top_fts = list(
            np.load(
                f'{save_dir}/top_shap_features.npy',
                allow_pickle=True))
    elif XAI_tool == "LIME":
        top_fts = list(
            np.load(
                f'{save_dir}/top_lime_features.npy',
                allow_pickle=True))
    else:
        shap = list(
            np.load(
                f'{save_dir}/top_shap_features.npy',
                allow_pickle=True))
        lime = list(
            np.load(
                f'{save_dir}/top_lime_features.npy',
                allow_pickle=True))
        top_fts = list(set(shap) & set(lime))
        # if the number of common elements is less, use all of lime features
        if len(top_fts) < top_k:
            shap = list(
                np.load(
                    f'{save_dir}/top_shap_features.npy',
                    allow_pickle=True))
            lime = list(
                np.load(
                    f'{save_dir}/top_lime_features.npy',
                    allow_pickle=True))
            top_fts = list(set(shap) | set(lime))[:top_k + 2]

    # ****************
    # get human interpretable feature labels
    # #initiate retriever, chain
    llm = ChatOpenAI(
        temperature=0.1,
        model_name="gpt-4",
        request_timeout=1000)

    prompt_fts = PromptTemplate(template=FORMAT_LABLES,
                                input_variables=["label"])
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    llm_fts = LLMChain(prompt=prompt_fts, llm=llm, memory=readonlymemory)
    new_labels = []
    for ft in top_fts:
        new_labels.append(llm_fts.run({'label': ft}))

    # *******************************
    # generate NLEs with citations

    features = ','.join(new_labels)
    docs = []
    # first collect docs for each feature
    for feature in new_labels:
        initial_question = f"""It has been identified by XAI analysis {feature} have an impact on the {observation}. \n
        Your task is to explain how the {observation} is affected by the {feature}. \
        How does each of these features impact the {observation}?
        """
        # Get relevant docs
        db = Chroma(persist_directory="./data/chroma/",
                    embedding_function=embedding)

        docs.append(db.max_marginal_relevance_search(initial_question))

    # flatten list of docs
    docs = [item for sublist in docs for item in sublist]
    # add citations from metadata
    documents = ""
    for i in range(len(docs)):
        doc = docs[i].page_content
        try:
            authors = docs[i].metadata["authors"]
            year = docs[i].metadata["year"]
            documents += f"{doc} ({authors},{year}) \n\n"
        except BaseException:
            documents += f"{doc} \n\n"

    prompt = PromptTemplate(
        template=REFINE_PROMPT,
        input_variables=[
            "documents",
            "features",
            "observation"])

    refine_chain = LLMChain(prompt=prompt, llm=llm)

    response = refine_chain.run({"documents": documents,
                                 "features": features,
                                 "observation": observation})

    return response
