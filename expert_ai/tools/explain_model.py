import json
from .utils import *

def get_modelsummary(json_request):
    '''
    Takes a dictionary as input in the form:
    { "data_path":"<path to dataframe>", 
    "label":"<target label>", 
    "model_type":<classifier or regressor>, 
    "top_k":<Number of features to explain>,
    "XAI_tool": <SHAP, LIME or Both>
    }.

    Example:
        {"data_path":".data/ft1034_labeldropped.csv",
        "label":"HAS_OMS",
        "model_type": "classifier",
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
        np.save(f'{save_dir}/top_shap_features.npy',top_shap_fts)
    else: shap_summary = ''
    #np.save(f'{save_dir}/top_shap_features.npy',top_fts)

    ## Step 3: Run Lime
    if XAI_tool == "LIME" or XAI_tool == "Both":
        top_lime_fts, lime_summary = explain_lime(data_path,model_path,model_type,
                                                  top_k,label)
        np.save(f'{save_dir}/top_lime_features.npy',top_lime_fts)
    else: lime_summary = ''


    ## Step 4: Generate explanation and create vectorstore
    f = open(f'{save_dir}/XAI_summary.txt',"w+")
    f.write(shap_summary+lime_summary)
    f.close()

    vector_db(lit_file=f'{save_dir}/XAI_summary.txt', clean=True)

    ## Step 5: Generate summary of model explanation
    prompt = f"""Summarize the following and explain the model
    from the following: {shap_summary+lime_summary}"""
    explanation = get_response(prompt)

    print(explanation)

    return explanation

    

    #st.write('Training complete')
    


"""request_format = '{{"data_path":"<path to dataframe>", "label":"<target label>", "model_type":<classifier or regressor>, "top_k":<Number of features to explain>,"XAI_tool": <SHAP, LIME or Both>}}'
description = f"""Train and Explain model. Input should be JSON in the following format:{request_format}."""

ExplainModel = Tool(
    name="explain_model",
    func=get_modelsummary,
    description=description
)

if __name__ == '__main__':
    print(ExplainModel)

"""
