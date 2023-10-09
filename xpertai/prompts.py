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

REFINE_PROMPT = """ It has been identified by XAI analysis {features} affect {observation}.
Your task is to go through given {documents} and their citations to explain the relationship between the  {features} and the {observation}
For example a document will have <text 1, (citation 1)>.
Combine these documents and generate a summarized answer.
Be precise and accurate as possible. Do not make up answers. 
Answer in a scientific manner.
Provide citations for the answer. A citation should be (Author, year)

You can use the following draft provide the summarized answer:
- Provide list of most impactful {features} found from the XAI analysis. If there are other features found in the literature provide them too.

- Describe the relationship of each feature in {features} with the {observation}. Critically evaluate your reasoning.

- Explain how each feature affect the {observation} and how the {observation} be altered by changing the features.
You must sound like a scientist. Give scientific reasoning for these answers.

- Next, provide a summary of the relationship between the {features} and the {observation}.

- Finally, provide the list the references in APA format:

"""