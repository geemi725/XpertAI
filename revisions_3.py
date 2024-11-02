from dotenv import load_dotenv
import pandas as pd
import shutil
import openai
import os
import sys

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key
from xpertai.tools.explain_model import get_modelsummary
from xpertai.tools.scrape_arxiv import scrape_arxiv
from xpertai.tools.generate_nle import gen_nle
from xpertai.tools.utils import vector_db

dataset_paths = "/Users/geemi/Geemi_docs/LIAC/revisions_xpertai/XpertAI/data/datasets"
datasets = {
    "OMS": ["Classifier", "presence of open metal sites in MOFs"],
    "PLD": ["Regressor", "pore limiting diameter in MOFs"],
    "TOX": ["Classifier", "toxicity of small molecules"],
    "SOL": ["Regressor", "solubility of small molecules"],
    "UFL": ["Regressor", "upper flammability limit of organic molecules"],
}
lit_path = "/Users/geemi/Geemi_docs/LIAC/revisions_xpertai/xprtai_2/literature"


for dataset, data in list(datasets.items())[0:3]:
    df_init = pd.read_csv(f"{dataset_paths}/{dataset}.csv", header=0)
    mode_type, observation = data
    print(dataset, mode_type, observation)
    XAI_tool = "SHAP"
    top_k = 3
    lit_files = f"{lit_path}/{dataset}"
    save_dir = f"./data_rd3/{dataset}"
    persist_directory = f"./data_rd3/{dataset}/chroma"

    for i in range(5):
        if i == 0:
            run_new = True
        else:
            run_new = False
            
        #run_new = True

        # create vectordb --DO ONLY ONCE
        if run_new:
            arg_dict_xai = {
                "df_init": df_init,
                "model_type": mode_type,
                "top_k": top_k,
                "XAI_tool": XAI_tool,
                "save_dir": save_dir,
                "persist_directory": persist_directory,
            }

            explanation = get_modelsummary(arg_dict_xai)

            for file in os.listdir(lit_files):
                if file.endswith(".pdf"):
                    try:
                        vector_db(
                            lit_file=os.path.join(lit_files, file),
                            try_meta_data=True,
                            persist_directory=persist_directory,
                        )
                    except:
                        print(f"vectordb failed for {file}!!")

        nle = gen_nle(
            {
                "observation": observation,
                "top_k": top_k,
                "XAI_tool": XAI_tool,
                "persist_directory": persist_directory,
                "save_dir": save_dir,
                "supporting_csv": f"{save_dir}/supporting_evidences_{i+1}.csv",
            }
        )
        # print(f"\n{'*' * 20} {nle} {'*' * 20}\n")
        with open(
            f"./data_rd3/{dataset}/structure_function_relationship_{i+1}.md", "w+"
        ) as f:
            f.write(f"Understanding {observation}:\n")
            f.write(nle)
            f.write(
                "\n\nExplanation generated with XpertAI. https://github.com/geemi725/XpertAI"
            )

    # print(explanation)
