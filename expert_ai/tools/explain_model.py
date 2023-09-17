from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
import json
import openai
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from .utils import *

def get_nle(json_request):
    '''Takes a JSON dictionary as input in the form:
    {"label":<target label>,
    "features": <list of features>}

    To explain for each feature in <features> affect <label> based on literature. 
    '''
    
    arg_dict = json.loads(json_request)
    label = arg_dict["label"]
    
    if "features" in arg_dict:
        features = arg_dict["features"]
    else: features=None
    
    merged_text = query_answers(label,features)

    llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo-0613",
            request_timeout=1000)
    # Split text
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(merged_text)
    # Create multiple documents
    docs = [Document(page_content=t) for t in texts]
    # Text summarization
    chain = load_summarize_chain(llm, chain_type='map_reduce')
    summary = chain.run(docs)
    with open('data/self_query_summary.txt','w+') as f:
        f.write(summary)
        f.close()

    prompt = f"""In this exercise you will assume the role of a scientific assistant. 
    Using {merged_text} write a critical evaluate the content.
    Explain what affect the {label}.
    The text should have an educative and assistant-like tone, be accurate.
    Explain how any conclusion is reached.
    """

    #messages = [{"role": "user", "content": prompt}]
    #response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613",
    #                                        messages=messages,temperature=0,)

    #summary = response.choices[0].message["content"]
    
    return summary
    


request_format = '{{"label":<target label>,"features": "<list of features>"}}'
description = f"""Input should be JSON in the following format:{request_format}."""

GetNLE = Tool(
    name="generate_NLE",
    func=get_nle,
    description=description
)

if __name__ == '__main__':
    print(GetNLE)


