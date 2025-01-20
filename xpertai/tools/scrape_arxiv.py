import arxiv
import re
import os
import shutil
from .utils import *


def scrape_arxiv(arg_dict):
    """Takes a  dictionary as input in the form:
    {"key_words":<key words to search arxiv>,
    "max_papers":<maximum number of papers to download>,
    "save_dir": <path to save downloaded papers>
    }

    Example:
        {"key_words":"MOF open metal sites",
        "max_papers":50,
        "save_dir":"./xpertai/data/arxiv_downloads"}


    returns:
        scrapes ArXiv for papers by given key words and download
    """

    for k, val in arg_dict.items():
        globals()[k] = val

    save_dir = "./data/lit_dir"
    if not lit_files:
        shutil.rmtree(save_dir)
        os.makedirs(save_dir)

    search = arxiv.Search(
        query=key_words, max_results=max_papers, sort_by=arxiv.SortCriterion.Relevance
    )

    for i, result in enumerate(search.results()):
        title = "_".join(result.title.split(" "))
        cleaned = re.sub(r"[^a-zA-Z0-9.]|(?<!\d)\.|\.(?!\d)", "_", title)
        result.download_pdf(dirpath=save_dir, filename=f"{cleaned}.pdf")
        if not lit_files and i == 0:
            clean = True
        else:
            clean = False

        # if lit files were given before then update vectordb (clean = False )otherwise create new
        vector_db(lit_file=f"{save_dir}/{cleaned}.pdf", clean=clean, try_meta_data=True)
