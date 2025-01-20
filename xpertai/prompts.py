FORMAT_LABLES = """
Given the label {label}, remove the integers. Using the label without integers, rewrite a new label
in a human interpretable manner. IMPORTANT: integer has no meaning! 
Return: new label

"""

REFINE_PROMPT = """
feature list: {features}
observation: {observation}

Documents: \n
{documents}

- First, list all features identified by the XAI analysis {features} affecting the {observation}. 
format: 
### Features Identified by XAI Analysis
- feature 1
- feature 2
...

You are an expert scientist. Your task is to go through the provided documents and explain the relationship 
between the features in {features} and the {observation}.
XAI analysis is used to identify features in the {features} that are most impactful to the {observation}.
Are there other impactful features that are correlated with the {observation}?

-Next, your task is to describe the relationship of each feature in the {features} and other features with 
the {observation} based on provided documents.\n
 Do the provided documents explicitly explain how each feature in the  {features} explicitly affects the 
 {observation}? If yes, provide the explanation.
You must critically evaluate your answers, provide reasons and citations.\n 
Each claim must be supported by scientific evidence. 
In line citations are required. \n eg: <claim (smith et al., 2020)> \n

Important: If the provided documents do not explicitly state the relationship between the feature 
and the observation, you must say "an explict relationship was not found in the given documents".\n 
Instead do the documents discuss about  synonymous features that are not identified by the XAI analysis? \n 
You can critically evaluate the relationship between such correlated with the {observation} and generate a 
hypothesis based on the information provided in the documents. \n 
Important: Each claim/hypothesis must be supported with citations. \n

Format:
#### <feature>: 
**Explanation**: <relationship of feature to the observation>
**Scientific Evidence** <provide scientific evidence/citations from the documents> 
**Hypothesis**: <your hypothesis>

- Then, provide a summary of everything you described previously to describe the relationship between these 
features and the {observation}. You must sound like a scientist.
  Give scientific evidence for these answers and provide citations.

- Finally, provide the list of references only used to answer. DO NOT make up references. 
Use APA style for referencing. \n
Eg: References: \n
    1. reference 1 \n
    2. reference 2 \n
    ...

"""

SUMMARIZE_PROMPT = """You are an expert scientist in chemistry. You are provided with an unformatted text excerpt from a journal article.\n
Your task is to  provide a clear and concise summary of the given text in a scientific manner. \n
IMPORTANT: You must not hallucinate extra information. You must only summarize the text provided. \n
text: {text}"""

SUMMARIZE_PROMPT_WITH_QUESTION = """You are an expert scientist in chemistry. You are provided with an unformatted text excerpt from a journal article.\n
Your task is to  provide a clear and concise summary of the given text in a scientific manner. \n
The excerpt is related to the following question: {question}
IMPORTANT: You must not hallucinate extra information. You must only summarize the text provided. \n
text: {text}"""
