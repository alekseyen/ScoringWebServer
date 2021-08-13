import os
import shutil
import time
from enum import Enum
from typing import Dict

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import optuna
import pandas as pd
from catboost import CatBoostClassifier
from catboost import Pool
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm

SEED = 42


class LearningType(str, Enum):
    SINGLE = "single"
    RANDOMIZED = "randomized"
    GRID = "grid"
    OPTUNA = "optuna"


CAT_FEATURES = [
    "region_x5",
    "region_rossvyaz",
    "loyalty_appl_form_status_code",
    "loyalty_card_status_dk",
    "loyalty_card_type_code",
    "gender_dk",
    "product",
]

DEFAULT_PARAMS = {"depth": 6, "learning_rate": 0.15, "iterations": 200}

DEFAULT_GRID_SEARCH = {
    "learning_rate": [0.03, 0.1],
    "depth": [4, 6, 10],
    "l2_leaf_reg": [1, 3, 5, 7, 9],
}

gini = lambda y_true, y_pred: 2 * roc_auc_score(y_true, y_pred) - 1


def do_actual_cat_features(df):
    ans = []
    for feat in df.columns:
        if feat in CAT_FEATURES:
            df[feat] = df[feat].astype(str)
            ans.append(feat)

    return ans


def optuna_learning(trial, train, y_train, test, y_test):
    # Parameters
    params = {
        "iterations": trial.suggest_int("iterations", 50, 300),
        "depth": trial.suggest_int("depth", 4, 10),
        "learning_rate": trial.suggest_loguniform("learning_rate", 0.01, 0.3),
        "random_strength": trial.suggest_int("random_strength", 0, 100),
        "bagging_temperature": trial.suggest_loguniform(
            "bagging_temperature", 0.01, 100.00
        ),
        "od_type": trial.suggest_categorical("od_type", ["IncToDec", "Iter"]),
        "used_ram_limit": "40gb",
    }
    # Learning
    model = CatBoostClassifier(
        loss_function="Logloss",
        eval_metric="AUC",
        l2_leaf_reg=50,
        random_seed=SEED,
        border_count=64,
        cat_features=do_actual_cat_features(train),
        **params,
    )
    model.fit(train, y_train, verbose=False)
    # Predict
    preds = model.predict_proba(test)[:, 1]
    ROC_AUC_Score = roc_auc_score(y_test, preds)
    print(f"test = {ROC_AUC_Score}")
    return ROC_AUC_Score


def run(
    df: pd.DataFrame,
    params: Dict = DEFAULT_PARAMS,
    search_type: LearningType = LearningType.SINGLE,
):
    cat_features = do_actual_cat_features(df)

    train, test, y_train, y_test = train_test_split(
        df.drop(columns=["target"]), df.target.astype(int), test_size=0.33
    )

    clf = CatBoostClassifier(
        eval_metric="AUC:hints=skip_train~false",
        loss_function="Logloss",
        cat_features=cat_features,
    )

    with mlflow.start_run():

        start_param_finding_time = time.time()

        if search_type == LearningType.GRID:
            params = clf.grid_search(
                DEFAULT_GRID_SEARCH, X=train, y=y_train, plot=True
            )["params"]

        if search_type == LearningType.RANDOMIZED:
            params = clf.randomized_search(
                DEFAULT_GRID_SEARCH, X=train, y=y_train, plot=True
            )["params"]

        if search_type == LearningType.OPTUNA:
            study = optuna.create_study(
                direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED)
            )
            study.optimize(
                lambda trial: optuna_learning(trial, train, y_train, test, y_test),
                n_trials=10,
            )

            params = study.best_trial.params

            print("optuna", params)

        mlflow.log_param("time_params_finding", time.time() - start_param_finding_time)

        clf = CatBoostClassifier(
            **params,
            eval_metric="AUC:hints=skip_train~false",
            cat_features=cat_features,
            loss_function="Logloss",
            early_stopping_rounds=10,
            random_state=SEED,
        )

        try:
            os.mkdir("graphs")
            os.mkdir("datasets")
        except:
            pass

        train.to_csv("datasets/train_dataset.gz", compression="gzip")
        test.to_csv("datasets/test_dataset.gz", compression="gzip")

        mlflow.log_artifacts("datasets", artifact_path="datasets")

        print("starting fit")

        start_fit_time = time.time()

        clf.fit(train, y_train, plot=True, verbose=False)

        mlflow.log_param("time_fit", time.time() - start_fit_time)

        ############## feature importance csv

        importance_df = pd.DataFrame(
            {
                "feature": clf.feature_names_,
                "importance": clf.get_feature_importance(
                    Pool(train, y_train, cat_features=cat_features)
                ),
            }
        )

        importance_df.sort_values(by=["importance"], ascending=False, inplace=True)
        importance_df.to_csv("graphs/importance.csv")

        ############## make predict

        do_actual_cat_features(test)
        y_pred_train = clf.predict_proba(train)[:, 1]
        y_pred_test = clf.predict_proba(test)[:, 1]

        plt.figure(figsize=(13, 8))
        plt.hist(y_pred_test, bins=500)
        plt.savefig("graphs/prediction_hist.png")

        ##############

        ##############

        mlflow.log_metric("roc-auc-test", roc_auc_score(y_test, y_pred_test))
        mlflow.log_metric("gini-test", gini(y_test, y_pred_test))

        mlflow.log_metric("roc-auc-train", roc_auc_score(y_train, y_pred_train))
        mlflow.log_metric("gini-train", gini(y_train, y_pred_train))

        mlflow.catboost.log_model(cb_model=clf, artifact_path="full_model")

        ### feature selection
        res = []
        features_num_interval = range(10, 51, 5)

        for features_num in tqdm(features_num_interval):
            clf = CatBoostClassifier(
                **params,
                eval_metric="AUC:hints=skip_train~false",
                loss_function="Logloss",
                early_stopping_rounds=10,
                random_state=SEED,
                verbose=False,
            )
            selector = SelectFromModel(estimator=clf, max_features=features_num).fit(
                train, y_train, cat_features=cat_features, plot=False, verbose=False
            )

            new_cat_features = set(CAT_FEATURES).intersection(
                train.columns[selector.get_support()]
            )
            X_train_new = train[train.columns[selector.get_support()]]
            X_test_new = test[test.columns[selector.get_support()]]

            cat_model = CatBoostClassifier(
                **params,
                cat_features=new_cat_features,
                eval_metric="AUC:hints=skip_train~false",
                verbose=False,
                random_state=SEED,
            )

            cat_model.fit(
                X_train_new,
                y_train,
                eval_set=(X_test_new, y_test),
                plot=False,
                verbose=False,
            )

            res.append(cat_model.get_best_score())

        train_metrics = np.array([measure["learn"]["AUC"] for measure in res])
        test_metrics = np.array([measure["validation"]["AUC"] for measure in res])

        plt.figure(figsize=(13, 8))
        plt.plot(features_num_interval, train_metrics, label="Train")
        plt.plot(features_num_interval, test_metrics, label="Test")
        plt.legend()
        plt.grid()
        plt.savefig("graphs/feature_num_plot.png")

        mlflow.log_artifacts("graphs", artifact_path="graphs")

        mlflow.log_param("catboost param", params)
        mlflow.log_param("dataset shape", df.shape)

        mlflow.log_param("learning type", search_type)
        ######## delete temp log folders

        shutil.rmtree("graphs", ignore_errors=True)
        shutil.rmtree("datasets", ignore_errors=True)

        run = mlflow.active_run()
        print("Active run_id: {}".format(run.info.run_id))


# run(pd.read_csv("../uploads/tcs04_example3k.csv").drop(columns=["Unnamed: 0"]), search_type=LearningType.OPTUNA)
# run(pd.read_csv('uploads/full_tcs04.csv').drop(columns=['Unnamed: 0']))
