from langchain.agents import Tool
from .utils import *
from langchain.embeddings.openai import OpenAIEmbeddings
embedding = OpenAIEmbeddings()
from langchain.vectorstores import Chroma

CUSTOM_TOOL_DOCS_SEPARATOR = "\n\n"

def retrieve_docs(query: str) -> str:
    '''
    Retrieve and search relevant documents to answer the query.
    1. Retrieve documents
    2. Compile expert answer from relevant documents. 
    3. Make a concise description as accurate as possible. Do not make up answers.
    4. Return summarized answer.
    
    '''

    vectordb = Chroma(persist_directory="./data/chroma/", 
                      embedding_function=embedding)
    retriever = vectordb.as_retriever()

    docs = retriever.get_relevant_documents(query)
    texts = [doc.page_content for doc in docs]
    texts_merged = CUSTOM_TOOL_DOCS_SEPARATOR.join(texts)

    return texts_merged



description = f"Retrieve answers to questions from literature. \
Provides summarized, human readable and factual answers."

RetriveInfo = Tool(
    name="retrieve_docs",
    func=retrieve_docs,
    description=description
)

if __name__ == '__main__':
    print(RetriveInfo)
