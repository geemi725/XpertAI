__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import json
import os
from PIL import Image 
from io import StringIO
import pandas as pd
from langchain.callbacks import StreamlitCallbackHandler
from dotenv import load_dotenv


load_dotenv()
ss = st.session_state

st.title("Xpert AI")
st.write('''### Extract structure-function relationships from your data!

This is a simple app which helps you to extract human interpretable relationships
in your dataset. ''')

# Set width of sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 800px;
        max-width: 800px;
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
                  on_change=on_api_key_change, label_visibility= "hidden")   
    

    st.markdown('## Upload your input dataset')
    input_file = st.file_uploader("Input to extract relationships from (must have .csv extention):")
    
    st.markdown('Set up XAI workflow')
    mode_type =  st.radio("Select the model type",
                           ["Regressor", "Classifier"],
                           captions= ["For predicting continuous values", "For predicting discreet labels"])
    label = st.text_input("Target label",
                          help='Label you are trying to predict. Should match the label in the dataset.')
    XAI_tool =  st.radio("What XAI method would you like to try?",
                           ["SHAP", "LIME","Both"])
    top_k =   st.slider('Number of top features for the XAI analysis', 0, 10, 1) 
    
    st.markdown("## Select method of literature retrieval. You can either upload a literature dataset or scrape arxiv.org. If you don't provide literature, you will receive an explanation based on XAI tools.")
    #lit_dir = st.file_uploader("Upload your literature library here (Optional):", 
    #                           accept_multiple_files=True)
    arxiv_keywords = st.text_input("Keywords for arxiv scraping:",
                                   help='Keywords to scrape arxiv.org')
    max_papers = st.number_input("Number of papers", key=int, value=10,
                          help='Maximum number of papers to download from arxiv.org')
    
    observation = st.text_input("What is the property you'd like explained?",
                                   help='e.g: Size of pore limiting diameter')
    
    button = st.button("Generate Explanation")

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
            nle = ''

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
                
                st.write("## The structure function relationship can be explained as belwo:\n", 
                     nle)


print(st.session_state)
# Agent execution
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        response = agent.run(query=prompt)
        st.write(response)
        '''st_callback = StreamlitCallbackHandler(
            st.container(),
            max_thought_containers = 4,
            collapse_completed_thoughts = False,
            output_placeholder=st.session_state
        )
'''
        