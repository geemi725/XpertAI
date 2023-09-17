from langchain.agents import Tool
import json
from .utils import *

def get_lime(lime_request: dict):

    '''
    Takes a JSON dictionary as input in the form:

    {"data_path":<path to data initial dataframe>, 
    "label":<target label>,
    "model_path":<model>,
    "top_k":<top number of features for SHAP analysis>,
    "save_dir":<path to save data>,
    "mode":<"classification" or "regression">
    "num_samples": <number of samples for LIME analysis>}

    parameters:
        lime_request : The JSON dictionary input string to initialize SHAP analysis
    '''
    kw_dict = {"top_k": 5, "num_samples":50,
                    "save_dir":'./data'}

    arg_dict = json.loads(lime_request)
    data_path = arg_dict["data_path"]
    label = arg_dict["label"]
    model_path = arg_dict["model_path"]
    mode = arg_dict['mode']

    for k,val in kw_dict.items():
        if k in arg_dict:
            globals()[k] = arg_dict[k]
        else:
            globals()[k] = val

    top_fts = explain_lime(data_path,label,model_path,mode=mode,
                  top_k=top_k,savedir=save_dir,num_samples=num_samples)
    
    
    return f"LIME analysis done! Most impactful features:{top_fts}"
   
    
request_format = '{{"data_path":<path to data initial dataframe>, "label":<target label>,"model_path":<model>,"top_k":<top number of features for SHAP analysis>, "save_dir":<path to save data>, "mode":<"classification" or "regression">, "num_samples": <number of samples for LIME analysis>}}'
description = f"Conduct LIME analysis and retrieve a summary of top k features. Input must be a JSON dictionary in the following format:{request_format}"

GetLIME = Tool(
    name="squeeze_lime🍋",
    func=get_lime,
    description=description
)

if __name__ == '__main__':
    print(GetLIME)