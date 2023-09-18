from langchain.agents import Tool
import json
from .utils import *
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def get_shap(shap_request: dict):

    '''
    Takes a JSON dictionary as input in the form:
    {"data_path":<path to data initial dataframe>, 
    "label":<target label>,
    "model_path":<model>,
    "model_type":<classifier or regressor>,
    "top_k":<top number of features for SHAP analysis>,
    }

    Example:
        {"data_path":"/data/wellawatte/mofs/expert_ai/data",
        "label":"HAS_OMS",
        "model_type": "classifier",
        "model_path": "/data/wellawatte/mofs/expert_ai/data/xgbmodel.json"
        "top_k": 5,
        }

    parameters:
        shap_request : The JSON dictionary input string to initialize SHAP analysis

    returns: 
        text of SHAP analysis summary
    '''

    arg_dict = json.loads(shap_request)

    for k,val in arg_dict.items():
        globals()[k] = val
    
    if model_type=='classifier': classifier=True
    else: classifier=False

    top_fts, shap_summary = explain_shap(data_path,model_path,label,top_k,classifier=classifier)
    #np.save(f'./data/top_shap_features.npy',top_fts)

    observation = f"""SHAP summary generated.\n 
    - Most impactful {top_k} features are: {top_fts}.\n
    - Initial model explanation:\n {shap_summary}.\n 
    - Ask the user to provide a literature dataset 
    - A literature dataset is compulsory to generate natural language explanations based on scientific evidence.\n
    - If the user does not have already have literature suggest scrape_arxiv tool.
        User can search papers in arxiv.org by specifying key words.\n
    - Additionally, users can interactively retrieve answers from literature.
    """
    print(f'Most impactful {top_k} features are: {top_fts}')
        
    return observation

request_format = '{{"data_path":<path to data initial dataframe>, "label":<target label>, "model_path":<trained model>,"model_type":<classifier or regressor>, "top_k":<top number of features for SHAP analysis>}}'
description = f"Conduct SHAP analysis and provide a summary of top k features. Input must be a JSON dictionary in the format {request_format}."

GetSHAP = Tool(
    name="get_shap",
    func=get_shap,
    description=description
)

if __name__ == '__main__':
    print(GetSHAP)