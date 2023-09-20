__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import json
import os
from PIL import Image 
from io import StringIO
import pandas as pd
from expert_ai.tools.utils import vector_db
from langchain.callbacks import StreamlitCallbackHandler
from dotenv import load_dotenv
load_dotenv()
ss = st.session_state

# Set width of sidebar
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
    api_key = ss.get('api_key') or os.getenv('OPENAI_API_KEY')
    #api_key = os.getenv('OPENAI_API_KEY')
    os.environ["OPENAI_API_KEY"] = api_key
    from expert_ai.tools import tools
    from expert_ai.agent import ExpertAI
    global agent    
    agent = ExpertAI(verbose=True)

## Header section
#logo = Image.open('assets/logo.png')
#st.image(logo)
st.title("Xpert AI")
st.write('''### Extract structure-function relationships from your data!

This is a simple app which helps you to extract human interpretable relationships
in your dataset. ''')
         
#tab1, tab2= st.tabs(['Setup', 'Explanations'])

with st.sidebar:
    logo = Image.open('assets/logo.png')
    st.image(logo)
    st.markdown('# Set up analysis :computer:')
    # Input OpenAI api key
    st.markdown('### Input your OpenAI API key.')
    api_key = st.text_input('OpenAI API key', type='password', key='api_key',  
                    on_change=on_api_key_change, label_visibility= "hidden")   


    st.markdown('### Upload your input dataset')
    input_file = st.file_uploader("Must have .csv extention:")

    st.markdown('### Set up XAI workflow')
    mode_type =  st.radio("Select the model type",
                            ["Regressor", "Classifier"],
                            captions= ["For predicting continuous values", "For predicting discreet labels"])
    label = st.text_input("Target label",
                            help='Label you are trying to predict. Should match the label in the dataset.')
    XAI_tool =  st.radio("What XAI method would you like to try?",
                            ["SHAP", "LIME","Both"])
    top_k =   st.slider('Number of top features for the XAI analysis', 0, 10, 1) 

    st.markdown("### Select method of literature retrieval \nYou can either upload a literature dataset or scrape arxiv.org. If you don't provide literature, you will receive an explanation based on XAI tools.")
    lit_files= st.file_uploader("Upload your literature library here (Optional):", 
                               accept_multiple_files=True)
    arxiv_keywords = st.text_input("Keywords for arxiv scraping:",
                                    help='Keywords to scrape arxiv.org')
    max_papers = st.number_input("Number of papers", key=int, value=10,
                            help='Maximum number of papers to download from arxiv.org')

    observation = st.text_input("What is the property you'd like explained?",
                                    help='e.g: Size of pore limiting diameter')

    button = st.button("Generate Explanation")


## Main page
if api_key:
    from expert_ai.tools.explain_model import get_modelsummary
    from expert_ai.tools.scrape_arxiv import scrape_arxiv
    from expert_ai.tools.generate_nle import gen_nle

if button:

    df_init = pd.read_csv(input_file,header=0)

    arg_dict_xai = { "df_init":df_init,
            "label":label, "model_type":mode_type, 
                "top_k":top_k, "XAI_tool": XAI_tool} 
    
    explanation =  get_modelsummary(arg_dict_xai)

    if XAI_tool=="SHAP":
        shap_bar = Image.open(f'./data/shap_bar.png')
        st.image(shap_bar)
    elif XAI_tool=="LIME":
        lime_bar = Image.open(f'./data/shap_bar.png')
        st.image(lime_bar)
    else:
        shap_bar = Image.open(f'./data/shap_bar.png')
        lime_bar = Image.open(f'./data/shap_bar.png')
        st.image(shap_bar)
        st.image(lime_bar)

    nle = ''

    ## read literature
    if lit_files is not None:
        for file in lit_files:
            try:
                pdf = file.read()#PyPDFLoader(file).load()
                #vector_db(lit_directory=None, persist_directory=None, 
                #    lit_file=file ,clean=False)
            except:
                st.write('coundnt read pdfs!!')


    # scrape arxiv.org
    if arxiv_keywords is not None:
        arg_dict_arxiv = {"key_words":arxiv_keywords,
                        "max_papers":max_papers}
        
        scrape_arxiv(arg_dict_arxiv)
    else: 
        st.write("## Literaure not provided. The initial XAI analysis is:\n", explanation)

    if observation is not None:
        arg_dict_nle = {"observation":observation,
                        "top_k":top_k, 
                        "XAI_tool": XAI_tool}
        nle = gen_nle(arg_dict_nle)
        
        st.write("## The structure function relationship can be explained as below:\n", 
                nle)

# sidebar
#with st.sidebar:
#logo = Image.open('assets/logo.png')
#st.image(logo)


