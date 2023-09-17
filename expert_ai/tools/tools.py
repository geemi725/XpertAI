from .train_model import TrainModel
from .explain_shap import GetSHAP
from .scrape_arxiv import ScrapeArxiv
from .retrieve_docs import RetriveInfo
from .explain_lime import GetLIME
from .generate_nle import GenNLE

def get_tools():
    all_tools = [
        TrainModel,
        GetSHAP,
        ScrapeArxiv,
        RetriveInfo,
        GetLIME,
        GenNLE,
    ]

    return all_tools