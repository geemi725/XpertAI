
import os
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
import openai
import re
import json


datasets = [ "OMS", "PLD", "TOX", "SOL", "UFL"]

lit_path = "/Users/geemi/Geemi_docs/LIAC/revisions_xpertai/xprtai_2/literature"


def get_response(prompt):

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
        )

    return response.choices[0].message["content"]

def get_metadata(lit_file):
    """'read page 1 of a pdf
    file and extract author, year,title
    for meta data"""
    reader = PdfReader(f"{lit_file}")
    page = reader.pages[0]
    text = page.extract_text()
    
    PROMPT =  """ You are given the first page of a journal article. Extract the list of author names, title, and year of publication from the following text: {text}.
    The goal is to generate metadata for the article in JSON format.

    Important: The output must be in JSON format with the following structure and nothing else:
    {{
    "Authors": "<author1, author2, ...>",
    "Year": "<year>",
    "Title": "<title>"
    }}
    """

    prompted = PROMPT.format(text=text)
    ## specific instructions to parse the output
    output = get_response(prompted)
    cleaned_output = re.sub(r'```json|```', '', output).strip()
    jdump = re.search(r'\{.*\}', cleaned_output, re.DOTALL).group(0)

    #jdump = "{" + jdump + "}"
    if jdump[0] != "{":
        jdump = "{" + jdump 
    if jdump[-1] != "}":
        jdump = jdump + "}"
    try: 
        metadatas = json.loads(jdump)
    except:
        print(f"metadata extraction failed for {lit_file}")
        jdump = {"Authors": lit_file, "Year": "FILL HERE", "Title": "FILL HERE"}
        metadatas = json.loads(jdump)

    return metadatas

for dataset in datasets:
    lit_files = f"{lit_path}/{dataset}"
    persist_directory = f"./data_rd3/{dataset}/chroma"
    with open(f"data_rd3/{dataset}_references.txt", "w") as f:
        for i, file in enumerate(os.listdir(lit_files)):
            if file.endswith(".pdf"):
                metadata = get_metadata(f"{lit_files}/{file}")
                authors = metadata["Authors"]
                year = metadata["Year"]
                title = metadata["Title"]
                f.write(f"{i+1}. {authors}, ({year}), {title}\n")