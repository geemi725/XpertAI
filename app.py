import streamlit as st
import pandas as pd
import os
from PIL import Image
import Ipython
#from Ipython.core.display import HTML
#from dotenv import load_dotenv

#load_dotenv()
#ss = st.session_state

st.title("Expert AI")
st.write('''### Extract structure-function relationships from your data!''')

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

'''def on_api_key_change():
    #api_key = ss.get('api_key') or os.getenv('OPENAI_API_KEY')
    api_key = os.getenv('OPENAI_API_KEY')
    os.environ["OPENAI_API_KEY"] = api_key


# sidebar
with st.sidebar:
    logo = Image.open('assets/logo.png')
    st.image(logo)

    # Input OpenAI api key
    st.markdown('Input your OpenAI API key.')
    st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_api_key_change, label_visibility="collapsed")'''