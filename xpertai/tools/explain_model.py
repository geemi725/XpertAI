import os
from .utils import *


def get_modelsummary(arg_dict):
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
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    # arg_dict = json.loads(json_request)
    for k, val in arg_dict.items():
        globals()[k] = val

    # Step 1: train model

    if model_type == "Classifier":
        train_xgbclassifier(df_init)

    elif model_type == 'Regressor':
        train_xgbregressor(df_init)

    model_path = f'{save_dir}/xgbmodel.json'

    # Step 2: Run SHAP Analysis
    if XAI_tool == "SHAP" or XAI_tool == "Both":
        if model_type == 'Classifier':
            classifier = True
        else:
            classifier = False

        top_shap_fts, shap_summary = explain_shap(df_init=df_init,
                                                  model_path=model_path,
                                                  top_k=top_k,
                                                  classifier=classifier)
        np.save(f'{save_dir}/top_shap_features.npy', top_shap_fts)
    else:
        shap_summary = ''
    # np.save(f'{save_dir}/top_shap_features.npy',top_fts)

    # Step 3: Run Lime
    if XAI_tool == "LIME" or XAI_tool == "Both":
        top_lime_fts, lime_summary = explain_lime(df_init=df_init,
                                                  model_path=model_path,
                                                  model_type=model_type,
                                                  top_k=top_k)
        np.save(f'{save_dir}/top_lime_features.npy', top_lime_fts)
    else:
        lime_summary = ''

    # Step 4: Generate explanation and create vectorstore
    f = open(f'{save_dir}/XAI_summary.txt', "w+")
    f.write(shap_summary + lime_summary)
    f.close()
    metadata = {'Authors': 'XpertAI', 'Year': '2023', 'Title': 'XAI Summary'}

    vector_db(lit_file=f'{save_dir}/XAI_summary.txt', clean=True,
              metadatas=metadata)

    # Step 5: Generate summary of model explanation
    prompt = f"""Summarize the following and explain the model
    from the following: {shap_summary+lime_summary}"""
    explanation = get_response(prompt)

    return explanation
