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

REFINE_PROMPT = """
feature list: {ft_list}
observation: {observation}

Your task is to go through {documents} and explain the relationship between the features in {ft_list} and the {observation}
XAI analysis is used to identify features in the <feature list> that are most impactful to the {observation}.
Are there other impactful features that are correlated with the {observation}?
    
You can follow the provided draft to answer:

- First, list all features identified by the XAI analysis <feature list> affecting the {observation}. List additional features that may be correlated with the {observation}.
\n Eg: {ft_list} found from the XAI analysis.

- Next, describe the relationship of each feature in the feature list with the {observation}. You must crtically evaluate your answers, provide reasons and citations.
  Eg:  solubility of a molecule is affected by the number of hydroxyl groups in the molecule. This is because hydroxyl groups are polar and can form hydrogen bonds with water molecules.

- Next, explain how each feature in the feature list affect the {observation} and how the {observation} be altered by changing the features.
  Eg: The solubility of a molecule can be increased by adding more hydroxyl groups to the molecule.

- Then, provide a summary of everything you described previously to describe the relationship between these features and the {observation}. You must sound like a scientist. 
  Give scientific evidence for these answers and provide citations.

- Finally, provide the list of references. Use APA citation style.
"""