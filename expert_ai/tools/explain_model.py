from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
import json
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import streamlit as st
from .utils import *

def get_modelsummary(json_request):
    '''
    Takes a dictionary as input in the form:
    { "data_path":"<path to dataframe>", 
    "label":"<target label>", 
    "model_type":<classifier or regressor>, 
    "top_k":<Number of features to explain>
    "XAI_tool": <SHAP, LIME or Both>
    }.

    Example:
        {"data_path":".data/ft1034_labeldropped.csv",
        "label":"HAS_OMS",
        "model_type": "classifier",
        "split":0.2,
        "top_k":5,
        "XAI_tool": "SHAP"
        }

    '''
    save_dir = './data'
    arg_dict = json.loads(json_request)
    for k,val in arg_dict.items():
        globals()[k] = val

    ##Step 1: train model
    
    if model_type=="classifier":
        train_xgbclassifier(data_path,label)
    
    else: 
        train_xgbregressor(data_path,label)
        
    model_path = f'{save_dir}/xgbmodel.json'

    ## Step 2: Run SHAP Analysis
    if XAI_tool == "SHAP" or XAI_tool == "Both":

        if model_type=='classifier': 
            classifier=True
        else: 
            classifier=False
        
        top_shap_fts, shap_summary = explain_shap(data_path,model_path,
                                            label,top_k,
                                            classifier=classifier)
    else: shap_summary = None
    #np.save(f'{save_dir}/top_shap_features.npy',top_fts)

    ## Step 3: Run Lime
    if XAI_tool == "LIME" or XAI_tool == "Both":
        top_lime_fts, lime_summary = explain_lime(data_path,model,mode,top_k,label)
    else: lime_summary = None


    ## Step 4: Generate explanation
    prompt = f"""Summarize the following and explain the model
    from the following: {shap_summary+lime_summary}"""
    
    explanation = get_response(prompt)

    return explanation, top_shap_fts, top_lime_fts

    

    #st.write('Training complete')
    


request_format = '{{"data_path":"<path to dataframe>", "label":"<target label>", "model_type":<classifier or regressor>, "top_k":<Number of features to explain>,"XAI_tool": <SHAP, LIME or Both>}}'
description = f"""Train and Explain model. Input should be JSON in the following format:{request_format}."""

ExplainModel = Tool(
    name="explain_model",
    func=get_modelsummary,
    description=description
)

if __name__ == '__main__':
    print(ExplainModel)


