
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
##from expert_ai.prompts import EXPLAIN_TEMPLATE
from .utils import *


def read_lit(file):

    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    persist_directory="./data/chroma/"
    doc = file.read()
   
    doc_split = r_splitter.split_documents(doc)
    vectordb = Chroma(persist_directory=persist_directory, 
                                    embedding_function=embedding)
                
    vectordb.add_documents(documents=doc_split ,
            embedding=embedding,
            persist_directory=persist_directory)
    
    vectordb.persist() 

    return "success"
