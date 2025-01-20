from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import LLMChain, PromptTemplate
from xpertai.prompts import REFINE_PROMPT, FORMAT_LABLES, SUMMARIZE_PROMPT
from .utils import *
from langchain.embeddings.openai import OpenAIEmbeddings
import pandas as pd

embedding = OpenAIEmbeddings()


def gen_nle(arg_dict):
    """Takes a dictionary as input in the form:
    {"observation":<target property>,
    "XAI_tool": <SHAP, LIME or Both>,
    "top_k":<maximum number of features to explain>
    "persist_directory":<path to vectordb>
    }

    Example:
    {"observation":"toxicity of small molecules",
    "XAI_tool": "SHAP",
    "top_k":3}
    """

    save_dir = "./data"
    global persist_directory
    persist_directory = "./data/chroma/"

    for k, val in arg_dict.items():
        globals()[k] = val

    # begin extracting information
    if XAI_tool == "SHAP":
        top_fts = list(np.load(f"{save_dir}/top_shap_features.npy", allow_pickle=True))
    elif XAI_tool == "LIME":
        top_fts = list(np.load(f"{save_dir}/top_lime_features.npy", allow_pickle=True))
    else:
        shap = list(np.load(f"{save_dir}/top_shap_features.npy", allow_pickle=True))
        lime = list(np.load(f"{save_dir}/top_lime_features.npy", allow_pickle=True))
        top_fts = list(set(shap) & set(lime))
        # if the number of common elements is less, use all of lime features
        if len(top_fts) < top_k:
            shap = list(np.load(f"{save_dir}/top_shap_features.npy", allow_pickle=True))
            lime = list(np.load(f"{save_dir}/top_lime_features.npy", allow_pickle=True))
            top_fts = list(set(shap) | set(lime))[: top_k + 2]

    # ****************
    # get human interpretable feature labels
    # #initiate retriever, chain
    llm = ChatOpenAI(temperature=0.0, model_name="gpt-4o", request_timeout=1000)

    prompt_fts = PromptTemplate(template=FORMAT_LABLES, input_variables=["label"])
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    llm_fts = LLMChain(prompt=prompt_fts, llm=llm, memory=readonlymemory)
    new_labels = []
    for ft in top_fts:
        new_labels.append(llm_fts.run({"label": ft}))

    # *******************************
    # generate NLEs with citations

    features = ",".join(new_labels)
    db = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    docs = []
    rows = []
    # first collect docs for each feature
    documents = ""
    for feature in new_labels:
        initial_question = f"""How is {feature} related to {observation}?"""
        # Get relevant docs
        fetched = db.max_marginal_relevance_search(initial_question, k=5)
        for document in fetched:
            doc = document.page_content
            summarize_prompt = PromptTemplate(
                template=SUMMARIZE_PROMPT, input_variables=["text"]
            )
            summarize_chain = LLMChain(prompt=summarize_prompt, llm=llm)
            summary = summarize_chain.run({"text": doc})

            try:
                authors = document.metadata["authors"]
                year = document.metadata["year"]
                title = document.metadata["source"]
                reference = f"REFERENCE:({authors},{year},{title})"
                documents += f"{summary} ({reference}) \n\n"
                rows.append(
                    {
                        "feature": feature,
                        "original": doc,
                        "summary": summary,
                        "reference": reference,
                    }
                )

            except BaseException:
                documents += f"{summary} \n\n"
                rows.append(
                    {
                        "feature": feature,
                        "original": doc,
                        "summary": summary,
                        "reference": "No reference found",
                    }
                )

    # write to csv
    # df = pd.DataFrame(rows)
    # df.to_csv(f"{supporting_csv}", index=False)

    # docs.append(fetched)

    prompt = PromptTemplate(
        template=REFINE_PROMPT, input_variables=["documents", "features", "observation"]
    )

    refine_chain = LLMChain(prompt=prompt, llm=llm)

    response = refine_chain.run(
        {"documents": documents, "features": features, "observation": observation}
    )

    return response
