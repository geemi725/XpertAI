
import os
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
import openai
import re
import json



datasets = {
    "OMS":  "presence of open metal sites in MOFs",
    "PLD": "pore limiting diameter in MOFs",
    "TOX":  "toxicity of small molecules",
    "SOL": "solubility of small molecules",
    "UFL": "upper flammability limit of organic molecules",
}


GPT_PROMPT = """

You are an expert scientist. Your task is to explain the relationship between the molecular features and the 
{observation}.

First, list all molecular features you think affect the {observation} and list them all. 
format: 
### Features Identified by ChatGPT
- feature 1
- feature 2
...

-Next, your task is to describe the relationship of each feature  with the {observation} based on your knowledge.\n
You must critically evaluate your answers and provide reasons.\n 
You can critically evaluate the relationship between correlated features with the {observation} and generate a 
hypothesis. \n 

Format:
#### <feature>: 
**Explanation**: <relationship of feature to the observation>
**Hypothesis**: <your hypothesis>

- Then, provide a summary of everything you described previously to describe the relationship between these 
features and the {observation}. You must sound like a scientist.

Finally, you must also provide a list of references to support your claims. Use APA style for referencing.\n
Eg: References: \n
    1. reference 1 \n
    2. reference 2 \n
    ...

"""
OLD_PROMPT = """Please explain how the property {observation} can be altered with respect to molecular features.
Your goal is to describe the relationship between molecular structure and the {observation}. """

def get_response(prompt):

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
        )

    return response.choices[0].message["content"]


for dataset, observation in datasets.items():
    prompt =  OLD_PROMPT.format(observation=observation)
    print("running", dataset)
    for i in range(1,6):
        with open(f"data_rd3/{dataset}/structure_function_relationship_baseline_{i}.md", "w") as f:
            output = get_response(prompt)
            f.write(output)
        
        print("finished", i)