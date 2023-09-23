__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import json
import os
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

    st.markdown("### Select method of literature retrieval \nIf you don't provide literature, you will receive an explanation based on XAI tools.")
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
    from expert_ai.tools.utils import vector_db

if button:

    df_init = pd.read_csv(input_file,header=0)

    arg_dict_xai = { "df_init":df_init,
            "label":label, "model_type":mode_type, 
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
                vector_db(lit_file=None)
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
        
        nle,new_ft_list = gen_nle(arg_dict_nle)

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

       

            

# sidebar
#with st.sidebar:
#logo = Image.open('assets/logo.png')
#st.image(logo)


