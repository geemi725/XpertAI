from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.memory.vectorstore import VectorStoreRetrieverMemory
from langchain import LLMChain, PromptTemplate
from expert_ai.prompts import EXPLAIN_TEMPLATE, FORMAT_LABLES
from .utils import *

def _update_db(lit_directory):
    vector_db(lit_directory=lit_directory)


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
    #arg_dict = json.loads(json_request)  
    for k,val in arg_dict.items():
        globals()[k] = val
    

    #initiate retriever, chain
    llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4",
            request_timeout=1000)
    

    db = Chroma(persist_directory="./data/chroma/", 
                      embedding_function=embedding)
    retriever = db.as_retriever()
    vectmem = VectorStoreRetrieverMemory(retriever=retriever,input_key="observation")
 
    #begin extracting information
    if XAI_tool=="SHAP":
        top_fts = list(np.load(f'{save_dir}/top_shap_features.npy',allow_pickle=True))
    elif XAI_tool=="LIME":
        top_fts = list(np.load(f'{save_dir}/top_lime_features.npy',allow_pickle=True))
    else:
        shap = list(np.load(f'{save_dir}/top_shap_features.npy',allow_pickle=True))
        lime = list(np.load(f'{save_dir}/top_lime_features.npy',allow_pickle=True))
        top_fts = list(set(shap) & set(lime))
        if len(top_fts)>top_k:
            top_fts[:top_k]
        
    ft_list = set([' '.join(ft.split('_')[:-1]) for ft in top_fts])

    #****************
    # get human interpretable feature labels
    prompt_fts = PromptTemplate(template=FORMAT_LABLES, 
                            input_variables=["label"])
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    llm_fts = LLMChain(prompt=prompt_fts, llm=llm, memory=readonlymemory)
    new_labels = []
    for ft in top_fts:
        new_labels.append(llm_fts.run({'label':ft}))


    #*******************************

    prompt_nle = PromptTemplate(template=EXPLAIN_TEMPLATE, 
                            input_variables=["observation","ft_list"])
    
    llm_nle = LLMChain(prompt=prompt_nle, llm=llm, memory=vectmem)
    response = llm_nle.run({'observation':observation,
                              'ft_list':ft_list
                              })

    #*******************************

    
    return response,new_labels

#request_format = '{{"lit_directory":"<path to literature>", "observation":<target property>}}'
#description = f"Tool to provide natural language explanations for the model based on scientific evidence. Provides reasoning on how each <feature> affects the <observation>. Input should be JSON in the following format: {request_format}. The output should be the answers to steps 1-5."


"""GenNLE = Tool(
    name="generate NLE",
    func=gen_nle,
    description=description
)

if __name__ == '__main__':
    print(GenNLE)"""