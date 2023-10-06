FORMAT_LABLES = """
Given the label {label}, remove the integers. Using the label without integers, rewrite the new label
in a human interpretable manner. IMPORTANT: integer has no meaning! Then return:
<new label> 

"""

EXPLAIN_TEMPLATE_NEW= """Please explain how each important features identified by 
    XAI analysis affects the observation {observation}. 
    Additionally, What are other impactful features that are correlated with the {observation}?
    Your goal is to describe the relationship between these features and the {observation}.
    
    You can follow the provided draft to answer:

    - List of most impactful features are identified by XAI analysis: {ft_list} and other features found from literature.
    
    - Describe the relationship of each feature in the {ft_list} with the {observation}. Crtically evaluate your reasonings.
    
    - Explain how each feature in the {ft_list} affect the {observation} and how the {observation} be altered by changing the <features>.

    - Finally, provide a summary of the relationship between these features and the {observation}.
    You must sound like a scientist. Give scientific reasoning for these answers.

    """

REFINE_PROMPT = """ Your task is to go through the multiple {documents}, their citations and explain the relationship between the given {features} and the {observation}
For example you will get <text 1, (citation 1)>, <text 2, (citation 2)>.
Combine these documents and generate a summarized answer.
Be precise and accurate as possible. Do not make up answers. 
Use the citations to generate a citation for the answer. Citations should be (Author, year)

You can use the following draft provide the summarized answer:
- List of most impactful {features}. If there are other features found in the literature provide them too.

- Describe the relationship of each feature in {features} with the {observation}. Crtically evaluate your reasonings.

- Explain how each feature affect the {observation} and how the {observation} be altered by changing the features.
You must sound like a scientist. Give scientific reasoning for these answers.

- Next, provide a summary of the relationship between the {features} and the {observation}.

- Finally, provide the list the references:
"""