from PIL import Image
from dotenv import load_dotenv
import pandas as pd
import shutil
import openai
import os
import streamlit as st
import sys
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
load_dotenv()
ss = st.session_state


st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 450px;
        max-width: 600px;
    }
    """,
    unsafe_allow_html=True,
)

def on_api_key_change():
    api_key = ss.get("api_key") or os.getenv("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = api_key
    openai.api_key = api_key

def save_uploadfile(uploadedfile):
    dirpath = os.path.join("data", "lit_dir")
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    with open(os.path.join(dirpath, uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())

st.write(
    "## Xpert AI: Extract human interpretable structure-property relationships from raw data"
)
st.write(
    """XpertAI trains a surrogate model to your dataset and extracts impactful features from your dataset using XAI tools.
Currently, GPT-4o model is used to generate natural language explanations."""
)

def run_autofill():
    st.session_state.auto_target = "toxicity of small molecules"
    st.session_state.auto_df = "tests/toxicity_sample_data.csv"
    st.experimental_rerun()

auto_target = st.session_state.get("auto_target", None)
auto_arxiv = st.session_state.get("auto_arxiv", None)

with st.sidebar:
    logo = Image.open("assets/logo_2.png")
    st.image(logo)
    # st.markdown('# Setup your inputs!')
    # Input OpenAI api key
    st.markdown("### First input your OpenAI API key :key:")
    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        key="api_key",
        on_change=on_api_key_change,
        label_visibility="hidden",
    )

    st.markdown("### Now upload your input dataset")
    input_file = st.file_uploader(
        "Dataset with featurized inputs & labels. Must have .csv extension AND the label column must be the last column of your dataset!"
    )

    st.markdown("### What is the target property you want to explain?")
    observation = st.text_input("eg.: Toxicity of small molecules", value=auto_target)

    st.markdown("### Set up XAI workflow")
    mode_type = st.radio(
        "1. Select the model type",
        [
            "Classifier",
            "Regressor",
        ],
        captions=["For predicting discreet labels", "For predicting continuous values"],
    )

    XAI_tool = st.radio("2. What's your favorite XAI method?", ["SHAP", "LIME", "Both"])
    top_k = st.slider(
        "3. Select the max number of features to be explained!", 0, 10, value=2
    )

    st.markdown(
        "### Provide literature to generate scientific explanations! \nIf you don't provide literature, you will receive an explanation based on XAI tools."
    )
    lit_files = st.file_uploader(
        "Upload your literature here. Files must be in `pdf` format (Suggested):", accept_multiple_files=True
    )
    arxiv_keywords = st.text_input(
        "If you want to scrape arxiv, provide keywords for arxiv scraping:",
        help="organic molecules, solubility of small molecules",
        value=auto_arxiv,
    )
    max_papers = st.number_input(
        "Maximum number of papers to download from arxiv.org", value=15
    )

    button = st.button("Generate Explanation", type="primary")

    st.markdown(
        "## Not sure what to do? Run a test case - explaining toxicity of small molecules!"
    )
    st.markdown(
        """**Make sure to add your OpenAPI key**. 
                You can download the input dataset after the explanation is generated.
                Literature is not scraped in this case."""
    )

    auto_button = st.button("Test Run", on_click=run_autofill)

# Main page
##set up the inputs
if auto_button:
    input_file = "./tests/toxicity_sample_data.csv"
    df_init = pd.read_csv(input_file, header=0)

    arg_dict_xai = {
        "df_init": df_init,
        "model_type": "Classifier",
        "top_k": top_k,
        "XAI_tool": XAI_tool,
    }

elif input_file and button:
    df_init = pd.read_csv(input_file, header=0)
    arg_dict_xai = {
        "df_init": df_init,
        "model_type": mode_type,
        "top_k": top_k,
        "XAI_tool": XAI_tool,
    }
else:
    arg_dict_xai = None

if button or auto_button:
    # validate api key
    if api_key.startswith("sk-"):
        from xpertai.tools.explain_model import get_modelsummary
        from xpertai.tools.scrape_arxiv import scrape_arxiv
        from xpertai.tools.generate_nle import gen_nle
        from xpertai.tools.utils import vector_db

    else:
        st.warning("Please enter a valid OpenAI API key!")
        st.stop()

    if arg_dict_xai is None:
        st.warning("Please upload a dataset!")
        st.stop()

    explanation = get_modelsummary(arg_dict_xai)

    st.markdown("### XAI Analysis:")
    xg_plot = Image.open(f"./data/figs/xgbmodel_error.png")
    st.image(xg_plot)

    if XAI_tool in ["SHAP", "LIME"]:
        st.image(Image.open(f"./data/figs/{XAI_tool.lower()}_bar.png"))
    else:
        st.image(Image.open(f"./data/figs/shap_bar.png"))
        st.image(Image.open(f"./data/figs/lime_bar.png"))

    if auto_button:
        shutil.copytree("./paper/datasets", "./data/figs", dirs_exist_ok=True)

    with st.spinner("Please wait...:computer: :speech_balloon:"):
        # read literature
        lit_files_given = False
        if lit_files:
            lit_files_given = True
            for file in lit_files:
                save_uploadfile(file)
                try:
                    vector_db(
                        lit_file=os.path.join("./data/lit_dir", file.name),
                        try_meta_data=True,
                        clean=True,
                    )
                except BaseException:
                    st.write("vectordb failed!!")

        # scrape arxiv.org
        if arxiv_keywords:
            arg_dict_arxiv = {"key_words": arxiv_keywords, "max_papers": max_papers,"lit_files":lit_files_given}

            scrape_arxiv(arg_dict_arxiv)

        if not arxiv_keywords and not lit_files:
            st.markdown(
                f"""### Literature is not provided to make an informed explanation. Based on XAI analysis, the following explanation can be given:
                \n{explanation}"""
            )
            nle = explanation

        else:
            # Generate evidence-based explanation
            nle = gen_nle(
                {
                    "observation": observation,
                    "top_k": top_k,
                    "XAI_tool": XAI_tool,
                }
            )

            st.write(
                "### The structure function relationship based on XAI analysis and literature, the following explanation can be given:\n",
                nle,
            )

        f = open("./data/figs/structure_function_relationship.txt", "w+")
        f.write(f"Understanding {observation}\n:")
        f.write(nle)
        f.write(
            "\n\nExplanation generated with XpertAI. https://github.com/geemi725/XpertAI"
        )
        f.close()

        shutil.make_archive("./data/figs", "zip", "./data/figs/")
        with open("./data/figs.zip", "rb") as f:
            st.download_button(
                "Download the outputs!", f, file_name="XpertAI_output.zip"
            )