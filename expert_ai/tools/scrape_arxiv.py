from langchain.agents import Tool
import arxiv
import re 
import os
import shutil
from .utils import *

#def _update_db(lit_directory):
#    vector_db(lit_directory=lit_directory)

def scrape_arxiv(arg_dict):
    '''Takes a  dictionary as input in the form:
    {"key_words":<key words to search arxiv>,
    "max_papers":<maximum number of papers to download>,
    "save_dir": <path to save downloaded papers>
    }

    Example:
        {"key_words":"MOF open metal sites",
        "max_papers":50,
        "save_dir":"/data/wellawatte/mofs/expert_ai/data/arxiv_downloads"}


    returns: 
        scrapes ArXiv for papers by given key words and download
    '''

    #arg_dict = json.loads(json_request)
    for k,val in arg_dict.items():
        globals()[k] = val

    save_dir = './data/downloads/'
    if os.path.exists(save_dir): 
        shutil.rmtree(save_dir )
    
    os.mkdir(save_dir)

    search = arxiv.Search(
        query = key_words,
        max_results = max_papers,
        sort_by = arxiv.SortCriterion.Relevance
    )
    
    for result in search.results():
        title = '_'.join(result.title.split(' '))
        cleaned = re.sub(r"[^a-zA-Z0-9.]|(?<!\d)\.|\.(?!\d)", "_",title)
        result.download_pdf(dirpath=save_dir, filename=f"{cleaned}.pdf")
        vector_db(lit_file=f'{save_dir}{cleaned}.pdf')

    #_update_db(save_dir)

    #return f"{max_papers} are downloaded from ArXiv and saved to {save_dir}"

#request_format = '{{"key_words":<key words to search arxiv>, "max_papers":<maximum number of papers to download>,"save_dir": <path to save downloaded papers>}}'
#description = f"Search arxiv.org for publications with given keywords and download. Input should be a JSON dictionary in the following format: {request_format}"

"""ScrapeArxiv = Tool(
    name="scrape_arxiv📃",
    func=scrape_arxiv,
    description=description
)

if __name__ == '__main__':
    print(ScrapeArxiv)
"""