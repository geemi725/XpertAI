import numpy as np
import os
import json
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from langchain.document_loaders import TextLoader
import xgboost as xgb
import shap
from lime.lime_tabular import LimeTabularExplainer
from scipy import stats
import shutil
import openai

# from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from pypdf import PdfReader


def _split_data(df_init):
    # for test dataset not all
    df_y = df_init.iloc[:, -1:]
    df_x = df_init.iloc[:, :-1]

    x_train, x_val, y_train, y_val = train_test_split(
        df_x, df_y, test_size=0.2, random_state=42
    )

    return x_train, x_val, y_train, y_val


def _plots(results, eval_type):
    figsave = "./data/figs/"

    if os.path.exists(figsave):
        shutil.rmtree(figsave)
    os.makedirs(figsave)

    x_axis = np.arange(len(results["validation_0"][eval_type]))
    fig, ax = plt.subplots()
    ax.plot(x_axis, results["validation_0"][eval_type], label="Train")
    ax.plot(x_axis, results["validation_1"][eval_type], label="Test")
    ax.legend()
    plt.ylabel(f"{eval_type.upper()}")
    plt.xlabel("Num iterations")
    plt.title(f"XGBoost model evaluation: {eval_type.upper()}")
    # plt.show()
    fig.savefig(f"{figsave}/xgbmodel_error.png")


def train_xgbclassifier(df_init, save_data=True, savedir=None):
    if savedir is None:
        savedir = "./data"
    early_stopping_rounds = 5

    x_train, x_val, y_train, y_val = _split_data(df_init=df_init)

    # initialize model
    eval_metric = ["auc", "error"]
    xgb_model = xgb.XGBClassifier(
        objective="binary:logistic",
        random_state=42,
        eval_metric=eval_metric,
        early_stopping_rounds=early_stopping_rounds,
        n_estimators=50,
    )

    xgb_model.fit(
        x_train, y_train, eval_set=[(x_train, y_train), (x_val, y_val)], verbose=False
    )

    results = xgb_model.evals_result()

    if save_data:
        _plots(results, "error")
        xgb_model.save_model(f"{savedir}/xgbmodel.json")
        np.save(f"{savedir}/xgb_results.npy", results)

    else:
        return results


def train_xgbregressor(df_init, save_data=True, savedir=None):
    if savedir is None:
        savedir = "./data"
    early_stopping_rounds = 5

    x_train, x_val, y_train, y_val = _split_data(df_init)

    # initialize model
    xgb_model = xgb.XGBRegressor(
        objective="reg:squarederror",
        random_state=42,
        early_stopping_rounds=early_stopping_rounds,
    )

    xgb_model.fit(
        x_train, y_train, eval_set=[(x_train, y_train), (x_val, y_val)], verbose=False
    )

    results = xgb_model.evals_result()

    if save_data:
        _plots(results, "rmse")
        xgb_model.save_model(f"{savedir}/xgbmodel.json")
        np.save(f"{savedir}/xgb_results.npy", results)
    else:
        return results


def get_response(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0,
    )

    return response.choices[0].message["content"]


def explain_shap(
    df_init, model_path, top_k, savedir=None, classifier=False, save_data=True
):
    if savedir is None:
        savedir = "./data"

    # use all data for the shap analysis
    df_x = df_init.iloc[:, :-1]

    feat_labs = list(df_x)
    model = xgb.Booster()
    model.load_model(model_path)

    results = np.load(f"{savedir}/xgb_results.npy", allow_pickle=True).item()

    # retrieve metrics from the last iteration
    # order: [train_auc,train_error,test_auc,test_err
    if classifier:
        met_exp = ["Train AUC", "Train Error", "Test AUC", "Test Error"]
        metrics = [
            results["validation_0"]["auc"][-1],
            results["validation_0"]["error"][-1],
            results["validation_1"]["auc"][-1],
            results["validation_1"]["error"][-1],
        ]
    else:
        met_exp = ["Train RMSE", "Test RMSE"]
        metrics = [
            results["validation_0"]["rmse"][-1],
            results["validation_1"]["rmse"][-1],
        ]

    # SHAP analysis
    explainer = shap.Explainer(model, df_x)
    shap_values = explainer(df_x)

    if save_data:
        fig, ax = plt.subplots(figsize=(4, 4))
        shap.summary_plot(
            shap_values, df_x, plot_type="bar", max_display=top_k, show=False
        )
        plt.title("SHAP analysis")
        plt.xlabel("Average impact")
        fig.savefig(f"{savedir}/figs/shap_bar.png", bbox_inches="tight", dpi=300)

    # compute average impact
    avg_impacts = shap_values.abs.mean(0).values
    top_fts_args = np.flip(np.argsort(avg_impacts))

    pearsons = {}
    avg_im = {}
    for i in top_fts_args[:top_k]:
        shap_y = shap_values[:, i].values
        data_x = shap_values[:, i].data
        ft = feat_labs[i]
        pearsons[ft] = np.corrcoef(data_x, shap_y)[0][1]
        avg_im[ft] = avg_impacts[i]

    summary = f"The model can be evaluated with the following metrics."

    for i, val in enumerate(metrics):
        summary += f"Model's {met_exp[i]} is {val}. "

    summary = f"The model can be explained with the following SHAP analysis."
    for k, v in pearsons.items():
        summary += f"Feature {k} has a correlation coefficient of  {v} with its SHAP values. \nThe average impact of {k} is {avg_im[k]}.\n "

    shap_summary = summary

    return list(pearsons.keys()), shap_summary


def explain_lime(
    df_init, model_path, model_type, top_k=2, savedir=None, save_data=True
):
    weights = []
    num_samples = 500
    if savedir is None:
        savedir = "./data"
    # use all data for the shap analysis
    df_x = df_x = df_init.iloc[:, :-1]  # df_init.drop(label,axis = 1)
    if len(df_x) < num_samples:
        num_samples = len(df_x)

    if model_type == "Classifier":
        class_names = [0, 1]
        mode = "classification"
    else:
        class_names = list(df_init.iloc[:, -1:].columns)[0]
        # [f'{label}']
        mode = "regression"

    explainer = LimeTabularExplainer(
        df_x.values,
        feature_names=list(df_x.columns),
        class_names=class_names,
        mode=mode,
    )

    df_sample = df_x.sample(num_samples)
    num_fts = len(list(df_x.columns))

    for i in range(len(df_sample)):
        if model_type == "Classifier":
            model = xgb.XGBClassifier()
            model.load_model(model_path)
            exp = explainer.explain_instance(
                df_sample.iloc[i],
                model.predict_proba,
                num_features=num_fts,
                top_labels=True,
            )
        else:
            model = xgb.XGBRegressor()
            model.load_model(model_path)
            exp = explainer.explain_instance(
                df_sample.iloc[i], model.predict, num_features=num_fts, top_labels=True
            )
        exp_map = exp.as_map()
        cls = list(exp_map.keys())[0]
        # sort weights otherwise they are printed from highest to lowest w
        exp_map[cls].sort(key=lambda x: x[0])
        ws = np.array(exp_map[cls])[:, -1]
        zscore = stats.zscore(ws)
        weights.append(zscore)

    global_w = np.sum(np.vstack(weights), axis=0)

    # get top k features from LIME values
    top_fts = np.array(df_x.columns)[abs(global_w).argsort()[-top_k:][::-1]]
    lime = global_w[abs(global_w).argsort()[-top_k:][::-1]]
    y_pos = np.arange(top_k)

    if save_data:
        # plot LIME analysis
        fig, ax = plt.subplots()
        ax.barh(y_pos, lime)
        ax.set_yticks(y_pos, labels=top_fts)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel("Z-score lime values")
        ax.set_ylabel("Features")
        ax.set_title("LIME analysis")
        fig.savefig(f"{savedir}/figs/lime_bar.png", bbox_inches="tight", dpi=300)

    # write summary of LIME analysis
    summary = f"To explain the model behavior, LIME explanations were generated. \
    \nPlease note these are global observations based on {num_samples} data points."

    for ft, l in zip(top_fts, lime):
        summary += f"Feature {ft} has an average\n \
             z-score of {l} with towards the prediction.\n"

    return top_fts, summary


def load_split_docs(filename, meta_data=None):
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, length_function=len
    )
    docs = None
    if filename.endswith(".pdf"):
        docs = PyPDFLoader(f"{filename}").load()

    elif filename.endswith(".txt"):
        docs = TextLoader(f"{filename}").load()

    docs_split = r_splitter.split_documents(docs)

    if meta_data is not None:
        for _docs in docs_split:
            _docs.metadata["source"] = meta_data["Title"]
            _docs.metadata["authors"] = meta_data["Authors"]
            _docs.metadata["year"] = meta_data["Year"]

    return docs_split


def _create_vecdb(docs_split, persist_directory, embedding):
    vectordb = Chroma.from_documents(
        documents=docs_split, embedding=embedding, persist_directory=persist_directory
    )

    vectordb.persist()


def _update_vecdb(docs_split, persist_directory, embedding):
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

    vectordb.add_documents(
        documents=docs_split, embedding=embedding, persist_directory=persist_directory
    )

    vectordb.persist()


def _get_metadata(lit_file):
    """'read page 1 of a pdf
    file and extract author, year,title
    for meta data"""
    reader = PdfReader(f"{lit_file}")
    page = reader.pages[0]
    text = page.extract_text()

    jdump = get_response(
        f""" Please extract list of author names, title, and
                           year of publication from this text {text}.
                           Output should have following format:
                           "Authors": "<author1, author2 ...>",
                           "Year": "<year>", "Title": "<title>"
                            """
    )

    jdump = "{" + jdump + "}"
    try: 
        metadatas = json.loads(jdump)
    except:
        metadatas = None

    return metadatas


def vector_db(
    persist_directory=None,
    lit_file=None,
    clean=False,
    try_meta_data=False,
    metadatas=None,
    embedding=None,
):
    if persist_directory is None:
        persist_directory = "./data/chroma/"

    if try_meta_data:
        metadatas = _get_metadata(lit_file)

    if embedding is None:
        embedding = OpenAIEmbeddings()

    text_split = load_split_docs(f"{lit_file}", meta_data=metadatas)

    if clean:
        # Delete and create persist directory
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        os.makedirs(persist_directory)
        _create_vecdb(text_split, persist_directory, embedding=embedding)

    else:
        _update_vecdb(text_split, persist_directory, embedding=embedding)
