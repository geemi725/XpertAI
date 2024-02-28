FORMAT_LABLES = """
Given the label {label}, remove the integers. Using the label without integers, rewrite a new label
in a human interpretable manner. IMPORTANT: integer has no meaning! 
Return: new label

"""

REFINE_PROMPT = """
feature list: {features}
observation: {observation}

Your task is to go through {documents} and explain the relationship between the features in {features} and the {observation}
XAI analysis is used to identify features in the {features} that are most impactful to the {observation}.
Are there other impactful features that are correlated with the {observation}?

You can follow the provided draft to answer:

- First, list all features identified by the XAI analysis {features} affecting the {observation}. List additional features that may be correlated with the {observation}.
\n Eg: {features} found from the XAI analysis.

- Next, describe the relationship of each feature in the {features} and other features with the {observation}. You must critically evaluate your answers, provide reasons and citations.
  Eg:  solubility of a molecule is affected by the number of hydroxyl groups in the molecule. This is because hydroxyl groups are polar and can form hydrogen bonds with water molecules. (Smith et al., 2019)

- Next, explain how each feature in the  {features} list affects the {observation} and how the {observation} be altered by changing the features.
  Eg: The solubility of a molecule can be increased by adding more hydroxyl groups to the molecule.

- Then, provide a summary of everything you described previously to describe the relationship between these features and the {observation}. You must sound like a scientist.
  Give scientific evidence for these answers and provide citations.

- Finally, provide the list of references only used to answer. DO NOT make up references. Use APA style for referencing. \n
Eg: References: \n
    1. reference 1 \n
    2. reference 2 \n
    ...
"""
