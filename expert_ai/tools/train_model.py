from langchain.agents import Tool
import json
from .utils import *

def train_model(json_request):
    '''
    Takes a JSON dictionary as input in the form:
    { "data_path":"<path to dataframe>", "label":"<target label>", 
    "split": <test split fraction>, "model_type":<classifier or regressor>, 
    "n_estimators":<number of estimators>, "early_stopping_rounds":<early stopping rounds>,
    }.

    Example:
        {"data_path":"/data/wellawatte/mofs/XAI/data/ft1034_labeldropped.csv",
        "label":"HAS_OMS",
        "model_type": "classifier",
        "split":0.2,
        "early_stopping_rounds": 10
        "n_estimators": 50
        }

    '''


    arg_dict = json.loads(json_request)
    for k,val in arg_dict.items():
        globals()[k] = val
    

    if model_type=="classifier":
        train_xgbclassifier(data_path,label,split,n_estimators,
                            early_stopping_rounds)
    
    else: 
        train_xgbregressor(data_path,label,split,
                            early_stopping_rounds=early_stopping_rounds)
        
    
    observation = f''''Next run a SHAP analysis for the trained model. 
    Use parameters: "data_path":{data_path},  "label":{label},
    "model_path":./data/xgbmodel.json, "top_k":5,"model_type":{model_type}
    ''' 

    return observation

request_format = '{{ "data_path":"<path to dataframe>","label":"<target label>","split": <test split fraction>, "model_type":<classifier or regressor>,"n_estimators":<number of estimators>, "early_stopping_rounds":<early stopping rounds>}}'
description = f"Train an XGBOOST Model from given data. Input should be JSON in the following format: {request_format}"

TrainModel = Tool(
    name="train_model🎪",
    func=train_model,
    description=description
)

if __name__ == '__main__':
    print(TrainModel)
