from .scrape_arxiv import ScrapeArxiv
from .retrieve_docs import RetriveInfo
from .generate_nle import GenNLE


def get_tools():
    all_tools = [
        ScrapeArxiv,
        RetriveInfo,
        GenNLE
    ]
    return all_tools