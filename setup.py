from setuptools import find_packages, setup

# for typing
__version__ = "0.0.0"
exec(open("expert_ai/version.py").read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="expert_ai",
    version=__version__,
    description="Extracting human innterpretable structure-function relationships with XAI",
    author="Geemi Wellawatte, Philippe Schwaller",
    author_email="geemi.wellawatte@epfl.ch",
    url="https://github.com/geemi725/expert-ai.git",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "ipython",
        "arxiv",
        "chromadb",
        "langchain",
        "tiktoken",
        "streamlit",
        "matplotlib",
        "numpy",
        "scikit-learn",
        "scipy",
        "shap",
        "xgboost"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)