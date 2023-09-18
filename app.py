import streamlit as st
import json
import os
from PIL import Image 
from io import StringIO

from langchain.callbacks import StreamlitCallbackHandler
from dotenv import load_dotenv

load_dotenv()
ss = st.session_state

st.title("Expert AI")
st.write('''### Extract structure-function relationships from your data!

This is a simple app which helps you to extract human interpretable relationships
in your dataset. ''')

# Set width of sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 450px;
        max-width: 450px;
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


# sidebar
with st.sidebar:
    logo = Image.open('assets/logo.png')
    st.image(logo)

    # Input OpenAI api key
    st.markdown('Input your OpenAI API key.')
    api_key = st.text_input('OpenAI API key', type='password', key='api_key',  
                  on_change=on_api_key_change, label_visibility= "collapsed")   
    

    st.markdown('Upload your input CSV files')
    input_file = st.file_uploader("Upload dataset here:")
    st.markdown('Set up XAI workflow')
    mode_type =  st.radio("Select the model type",
                           ["Regressor", "Classifier"],
                           captions= ["For predicting continuous values", "For predicting discreet labels"])
    label = st.text_input("Target label",
                          help='Label you are trying to predict. Should match the label in the dataset.')
    XAI_tool =  st.radio("What XAI method would you like to try?",
                           ["SHAP", "LIME","Both"])
    top_k =   st.slider('Number of top features for the XAI analysis', 0, 10, 1) 
    
    st.markdown("Select method of literature retrieval. You can either upload a literature dataset or scrape arxiv.org. If you don't provide literature, you will receive an explanation based on XAI tools.")
    lit_dir = st.file_uploader("Upload your literature library here (Optional):", 
                               accept_multiple_files=True)
    arxiv_keywords = st.text_input("Keywords for arxiv scraping (Optional):",
                                   help='Keywords to scrape arxiv.org')
    button = st.button("Generate Explanation")

    if api_key:
        on_api_key_change() 
        from expert_ai.tools.explain_model import get_modelsummary
        if button:
            bytes_data = input_file.getvalue()
            #stringio = StringIO(input_file.getvalue().decode("utf-8"))
            
            arg_dict = { "data_path":input_file , 
                    "label":label, "model_type":mode_type, 
                        "top_k":top_k, "XAI_tool": XAI_tool} 
            explanation =  get_modelsummary(arg_dict)
            #json_request = json.dumps(arg_dict, indent=4)
                
            st.write('god bless!!!')
            #if button:
            #    explanation =  get_modelsummary(json_request)
            #    st.write(explanation)
