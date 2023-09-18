#from .train_model import TrainModel
#from .explain_shap import GetSHAP
from .scrape_arxiv import ScrapeArxiv
from .retrieve_docs import RetriveInfo
#from .explain_lime import GetLIME
#from .generate_nle import GenNLE
#from .explain_model import ExplainModel

def get_tools():
    all_tools = [
        ScrapeArxiv,
        RetriveInfo
    ]
    return all_tools