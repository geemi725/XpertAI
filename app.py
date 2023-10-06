__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
import openai
from PIL import Image 
import shutil
import pandas as pd
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
    openai.api_key = api_key

def save_uploadfile(uploadedfile):
     
     dirpath = os.path.join('data','lit_dir')

     if os.path.exists(dirpath):
         shutil.rmtree(dirpath)
     os.mkdir(dirpath) 
     with open(os.path.join(dirpath,uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())

## Header section
#logo = Image.open('assets/logo.png')
#st.image(logo)
st.write("## Xpert AI: Extract human interpretable structure-property relationships from raw data")
st.write('''XpertAI trains a surrogate model to your dataset and extracts impactful features from your dataset using XAI tools.
Currently, GPT-4 model is used to generate natural language explanations.''')
         
#tab1, tab2= st.tabs(['Setup', 'Explanations'])

with st.sidebar:
    logo = Image.open('assets/logo.png')
    st.image(logo)
    #st.markdown('# Setup your inputs!')
    # Input OpenAI api key
    st.markdown('### First input your OpenAI API key :key:')
    api_key = st.text_input('OpenAI API key', type='password', key='api_key',  
                    on_change=on_api_key_change, label_visibility= "hidden")   


    st.markdown('### Now upload your input dataset')
    input_file = st.file_uploader("Must have .csv extention AND the label column must be the last column of your dataset!")

    st.markdown('### Set up XAI workflow')
    mode_type =  st.radio("1. Select the model type",
                            ["Regressor", "Classifier"],
                            captions= ["For predicting continuous values", "For predicting discreet labels"])
    #label = st.text_input("Target label",
    #                        help='Label you are trying to predict. Should match the label in the dataset.')
    XAI_tool =  st.radio("2. What's your favorite XAI method?",
                            ["SHAP", "LIME","Both"])
    top_k =   st.slider('3. Select the max number of features to be explained!', 0, 10, 1) 

    st.markdown("### Provide literature to generate scientific explanations! \nIf you don't provide literature, you will receive an explanation based on XAI tools.")
    lit_files= st.file_uploader("Upload your literature library here (Suggested):", 
                               accept_multiple_files=True)
    arxiv_keywords = st.text_input("If you want to scrape arxiv, provide keywords for arxiv scraping:",
                                    help='organic molecules, solubility of small molecules')
    max_papers = st.number_input('Maximum number of papers to download from arxiv.org', key=int, value=10)

    observation = st.text_input("What is the property you'd like explained?",
                                    help='solubility of small molecules')

    button = st.button("Generate Explanation")


## Main page
if api_key:
    from xpertai.tools.explain_model import get_modelsummary
    from xpertai.tools.scrape_arxiv import scrape_arxiv
    from xpertai.tools.generate_nle import gen_nle
    from xpertai.tools.utils import vector_db

if button:

    df_init = pd.read_csv(input_file,header=0)
    #"label":label,
    arg_dict_xai = { "df_init":df_init,
             "model_type":mode_type, 
                "top_k":top_k, "XAI_tool": XAI_tool} 
    
    explanation =  get_modelsummary(arg_dict_xai)
    
    st.markdown('### XGBoost Model evaluation:')
    xg_plot = Image.open(f'./data/figs/xgbmodel_error.png')
    st.image(xg_plot)

    if XAI_tool=="SHAP":
        shap_bar = Image.open(f'./data/figs/shap_bar.png')
        st.image(shap_bar)
    elif XAI_tool=="LIME":
        lime_bar = Image.open(f'./data/figs/lime_bar.png')
        st.image(lime_bar)
    else:
        shap_bar = Image.open(f'./data/figs/shap_bar.png')
        lime_bar = Image.open(f'./data/figs/lime_bar.png')
        st.image(shap_bar)
        st.image(lime_bar)

    

    nle = ''

    ## read literature
    if lit_files is not None:
        for file in lit_files:   
            save_uploadfile(file)
            filepath = os.path.join('./data/lit_dir',file.name)
            try:
                vector_db(lit_file=filepath,
                          try_meta_data=True)
            except: st.write('vectordb failed!!')
            
    # scrape arxiv.org
    if arxiv_keywords is not None:
        arg_dict_arxiv = {"key_words":arxiv_keywords,
                        "max_papers":max_papers}
        
        scrape_arxiv(arg_dict_arxiv)

    if observation is not None:
        arg_dict_nle = {"observation":observation,
                        "top_k":top_k, 
                        "XAI_tool": XAI_tool}
        
        nle = gen_nle(arg_dict_nle)

        if arxiv_keywords is None and lit_files is None:
            st.markdown(f"""### Literature is not provided to make an informed explanation.\n 
                        Based on XAI analysis, the following explanation can be given:
                        \n{explanation}""")
            st.download_button("Download the explanation!", 
                            data =explanation)
            f = open("./data/figs/structure_function_relationship.txt",'w+')
            f.write(f'Understanding {observation}\n:')
            f.write(explanation)
            f.close()

            
        else:
            st.write("### The structure function relationship based on XAI analysis and literature, the following explanation can be given:\n", 
                nle)
            f = open("./data/figs/structure_function_relationship.txt",'w+')
            f.write(f'Understanding {observation}\n:')
            f.write(nle)
            f.close()
        
            #st.download_button("Download the explanation!", 
            #                data =nle)
            
        shutil.make_archive('./data/figs', 'zip', './data/figs/')
        with open('./data/figs.zip', 'rb') as f:
            st.download_button('Download the explanation and figures', f, file_name='Figures.zip')



