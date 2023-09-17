
from langchain.agents import Tool
import json
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from paperqa import Docs
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
embedding = OpenAIEmbeddings()
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
##from expert_ai.prompts import EXPLAIN_TEMPLATE
from .utils import *
from .retrieve_docs import retrieve_docs
#from expert_ai.agent import ExpertAI
#agent = ExpertAI()

def suggest_improvement(input_request):
    '''Takes a JSON dictionary as input in the form:
    { "save_dir":<path to save data>,
    "observation":<target property>}
    
    Example:
    { "save_dir":"/data/wellawatte/mofs/expert_ai/data",
    "observation":"presense of open metal sites"}
    '''

    arg_dict = json.loads(input_request)
    for k,val in arg_dict.items():
        globals()[k] = val
    top_shap = list(np.load(f'{save_dir}/top_shap_features.npy',allow_pickle=True))

    llm = ChatOpenAI(
            temperature=0.,
            model_name="gpt-4",
            request_timeout=1000)
    
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)

    db = Chroma(persist_directory="./data/chroma/", 
                      embedding_function=embedding)
    retriever = db.as_retriever()
    chain =  ConversationalRetrievalChain.from_llm(llm, 
                                                   retriever=retriever, 
                                                   memory=readonlymemory,
                                                   )

    merged_text = ' ' 
    ft_lits = []
    for ft in top_shap:
        feature = ' '.join(ft.split('_')[:-1])
        ft_lits.append(feature)

        query = f"""
        Answer the following questions.  Explain how any conclusion is reached.
        Use the answers to the following questions to understand how the {observation}
        can be manipulated by the {feature}
        ``
        Q1. What is the relationship between {feature} and the {observation}?
        Q2. How does the {feature} impact the {observation}?
        Q3. How can the {observation} be improved by changing the {feature}?
        ``
        Final answer:
        
        """
        #response = retrieve_docs(query)
        response = chain.run(query)    
        #response = agent.run(query=query)
        merged_text += response

    text_splitter = RecursiveCharacterTextSplitter()
    texts = text_splitter.split_text(merged_text)
    db.add_texts(texts)
    retriever = db.as_retriever()
    chain =  ConversationalRetrievalChain.from_llm(llm, 
                                                   retriever=retriever, 
                                                   memory=readonlymemory,
                                                   )
    
    prompt = f'''f"Explain how the {observation} be improved. Which features in {ft_lits} are impactful?
    How can these features affect the {observation}. Provide complementary information to help generate conclusions.
    The text should have an educative and assistant-like tone! Be accurate "
    '''
    suggestion = chain.run(prompt)   

    return f'{suggestion}' 



    
request_format = '{{"save_dir":<path to save data>,"observation":<target property>}}'
description = f"Explain observation and suggest how to improve the observation. Input should be JSON in the following format: {request_format}"

SuggestImprovement = Tool(
    name="suggest_improvement",
    func=suggest_improvement,
    description=description
)

if __name__ == '__main__':
    print(SuggestImprovement)
