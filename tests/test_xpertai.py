import numpy as np
import pandas as pd
import sys
sys.path.append('../')
from xpertai.tools.utils import *

def test_train_xgbclassifier():
    df = pd.DataFrame(np.random.randint(0, 2, size=(100, 3)),
                      columns=['feature_1', 'feature_2', 'feature_3'])
    df['Target'] = np.random.randint(0, 2, size=(100, 1))
    results = train_xgbclassifier(df, save_data=False)
    assert results['validation_0']['error'] is not None


def test_train_xgbregressor():
    df = pd.DataFrame(np.random.randint(0, 2, size=(100, 3)),
                      columns=['feature_1', 'feature_2', 'feature_3'])
    df['Target'] = np.random.uniform(0, 2, (100, 1))

    results = train_xgbregressor(df, save_data=False)
    assert results['validation_0']['rmse'] is not None


def test_load_split_docs():
    base_dir = os.path.dirname(os.path.realpath('__file__'))
    doc_path = os.path.join(base_dir, 'tests/paper_test.pdf')
    docs_split = load_split_docs(doc_path)
    assert isinstance(docs_split[0].page_content, str)


def test_explain_shap():
    base_dir = os.path.dirname(os.path.realpath('__file__'))
    df = pd.DataFrame(np.random.randint(0, 2, size=(100, 3)),
                      columns=['feature_1', 'feature_2', 'feature_3'])
    df['Target'] = np.random.randint(0, 2, size=(100, 1))
    keys, summary = explain_shap(df, model_path=f'{base_dir}/tests/xgbmodel.json',
                                 top_k=1, savedir=f'{base_dir}/tests',
                                 classifier=True, save_data=False)

    assert summary is not None
    assert isinstance(keys, list)


def test_explain_lime():
    base_dir = os.path.dirname(os.path.realpath('__file__'))
    df = pd.DataFrame(np.random.randint(0, 2, size=(100, 3)),
                      columns=['feature_1', 'feature_2', 'feature_3'])
    df['Target'] = np.random.randint(0, 2, size=(100, 1))
    keys, summary = explain_lime(df, model_path=f'{base_dir}/tests/xgbmodel.json',
                                 model_type='Classifier',
                                 top_k=1, savedir=f'{base_dir}/tests',
                                 save_data=False)
    assert summary is not None
    assert keys is not None
