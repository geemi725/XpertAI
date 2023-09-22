GENERAL_TEMPLATE ="""You will assume the the role of a scientific assistant. 
The solution draft follows the format "Thought, Action, Action Input, Observation", where the 'Thought' statements describe a reasoning sequence.
Your task is to Process the {query} as best you can based on the solution draft.
The answer should have an educative and assistant-like tone, be accurate.
"""

FORMAT_LABLES = """
Given the label {label}, remove the integers. Using the label without integers, rewrite the new label
in a human interpretable manner. IMPORTANT: integer has no meaning! Then return:
<new label> 

"""
#For each part of your answer, indicate which sources most support it via valid citation markers at the end of each sentence, like (Example2012).
EXPLAIN_TEMPLATE= """Please explain how each important features identified by 
    XAI analysis affects the observation {observation}. 
    

    You can follow the provided draft to answer:

    1. List of most impactful features are identified by XAI analysis: {ft_list}.
    
    2. Find the relationship of the <features> with the {observation}
    eg:
    ``The relationship of <feature 1> with the {observation} is ...
      The relationship of <feature 2> with the {observation} is ...
      The relationship of <feature 3> with the {observation} is ... ``
    
    3. Explain how the <feature> affect the {observation}
    eg:
    ``<feature 1> affect the {observation} by ...
      <feature 2> affect the {observation} by ...
      <feature 3> affect the {observation} by ... ``
    
    4. Explain how the {observation} be altered by changing the <features>
    eg:
    ``The {observation} will change postively/negatively when <feature 1> changes because...
      The {observation} will change postively/negatively when <feature 2> changes because...
      The {observation} will change postively/negatively when <feature 3> changes because...
    
    5. Assume the role of a scientific assistant and summarize answers in steps 1-4. 
    Explain on how the {observation}  can be altered with respect to all the features: {ft_list}. 
    Give scientific reasoning for these answers.

    6. Add a list the sources used for generating answers. If you cannot find a sources avoid references.
    For further study:
    eg:
    ``<Reference 1>
      <Reference 2>
    ``


    """
