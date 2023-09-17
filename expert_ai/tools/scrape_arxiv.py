from langchain.agents import Tool
import json
import arxiv
import re 

def scrape_arxiv(json_request):
    '''Takes a JSON dictionary as input in the form:
    {"key_words":<key words to search arxiv>,
    "max_papers":<maximum number of papers to download>,
    "save_dir": <path to save downloaded papers>
    }

    Example:
        {"key_words":"MOF open metal sites",
        "max_papers":50,
        "save_dir":"/data/wellawatte/mofs/expert_ai/data/arxiv_downloads"}
    
    parameters:
        json_request (str): The JSON dictionary input string.

    returns: 
        scrapes ArXiv for papers by given key words
    '''

    arg_dict = json.loads(json_request)
    key_words = arg_dict["key_words"]
    max_papers = arg_dict["max_papers"]
    save_dir = arg_dict["save_dir"]

    search = arxiv.Search(
        query = key_words,
        max_results = max_papers,
        sort_by = arxiv.SortCriterion.Relevance
    )
    
    for result in search.results():
        title = '_'.join(result.title.split(' '))
        cleaned = re.sub(r"[^a-zA-Z0-9.]|(?<!\d)\.|\.(?!\d)", "_",title)
        result.download_pdf(dirpath=save_dir+'/', filename=f"{cleaned}.pdf")

    return f"{max_papers} are downloaded from ArXiv and saved to {save_dir}"

request_format = '{{"key_words":<key words to search arxiv>, "max_papers":<maximum number of papers to download>,"save_dir": <path to save downloaded papers>}}'
description = f"Search arxiv.org for publications with given keywords and download. Input should be a JSON dictionary in the following format: {request_format}"

ScrapeArxiv = Tool(
    name="scrape_arxiv📃",
    func=scrape_arxiv,
    description=description
)

if __name__ == '__main__':
    print(ScrapeArxiv)
