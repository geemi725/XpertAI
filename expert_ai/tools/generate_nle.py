import json
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.memory.vectorstore import VectorStoreRetrieverMemory
from langchain.chains import ConversationalRetrievalChain
from langchain import LLMChain, PromptTemplate
from expert_ai.prompts import EXPLAIN_TEMPLATE
import pandas as pd
from .utils import *

def _update_db(lit_directory):
    vector_db(lit_directory=lit_directory)


def gen_nle(json_request):
    '''Takes a JSON dictionary as input in the form:
    { "lit_directory:"<path to literature>",
    "observation":<target property>
    }

    Example:
    {"lit_directory:"data/arxiv_downloads"}

    parameters:
        json_request (str): The JSON dictionary input string.

    '''

    save_dir = './data'
    arg_dict = json.loads(json_request)  
    for k,val in arg_dict.items():
        globals()[k] = val
    
    #create a vector store from literature
    # Do only once (time consuming)
    _update_db(lit_directory)

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
    top_shap = list(np.load(f'{save_dir}/top_shap_features.npy',allow_pickle=True))
    ft_list = set([' '.join(ft.split('_')[:-1]) for ft in top_shap])

    #*******************************

    prompt = PromptTemplate(template=EXPLAIN_TEMPLATE, 
                            input_variables=["observation","ft_list"])
    
    llm_chain = LLMChain(prompt=prompt, llm=llm, memory=vectmem)
    response = llm_chain.run({'observation':observation,
                              'ft_list':ft_list
                              })

    #*******************************
    print(response)
    
    return f'Final explanation is: {response}. Provide the response as is.'

request_format = '{{"lit_directory":"<path to literature>", "observation":<target property>}}'
description = f"Tool to provide natural language explanations for the model based on scientific evidence. Provides reasoning on how each <feature> affects the <observation>. Input should be JSON in the following format: {request_format}. The output should be the answers to steps 1-5."


GenNLE = Tool(
    name="generate NLE",
    func=gen_nle,
    description=description
)

if __name__ == '__main__':
    print(GenNLE)