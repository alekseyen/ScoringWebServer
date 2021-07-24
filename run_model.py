import os
import pandas as pd
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier, Pool
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
import mlflow
import shap
import matplotlib.pyplot as plt
from typing import Dict
import shutil
import numpy as np

CAT_FEATURES = ['region_x5', 'region_rossvyaz', 'loyalty_appl_form_status_code',
                'loyalty_card_status_dk', 'loyalty_card_type_code', 'gender_dk']
DEFAULT_PARAMS = {
            'depth': 6,
            'learning_rate': 0.15,
            'iterations': 200}
gini = lambda y_true, y_pred: 2 * roc_auc_score(y_true, y_pred) - 1

def do_actual_cat_features(df):
    ans = []
    for feat in df.columns:
        if feat in CAT_FEATURES:
            df[feat] = df[feat].astype(str)
            ans.append(feat)

    return ans


def run(df: pd.DataFrame,
        params: Dict = DEFAULT_PARAMS):

    cat_features = do_actual_cat_features(df)
    train, test = train_test_split(df, test_size=0.25)

    train_data = Pool(data=train.drop(columns=['target']),
                      label=train.target.astype(int),
                      cat_features=cat_features)

    test_data = Pool(data=test.drop(columns=['target']),
                     cat_features=cat_features)

    clf = CatBoostClassifier(
        **params,
        eval_metric='AUC:hints=skip_train~false',
        loss_function='Logloss',
        early_stopping_rounds=10,
        random_state=13,
    )

    clf.fit(train_data)

    _ = do_actual_cat_features(test)

    y_pred_test = clf.predict_proba(test_data)[:, 1]
    y_true_test = test.target.astype(int)

    y_pred_train = clf.predict_proba(train_data)[:, 1]
    y_true_train = train.target.astype(int)

    with mlflow.start_run():
        mlflow.log_metric('roc-auc-test', roc_auc_score(y_true_test, y_pred_test))
        mlflow.log_metric('gini-test', gini(y_true_test, y_pred_test))

        mlflow.log_metric('roc-auc-train', roc_auc_score(y_true_train, y_pred_train))
        mlflow.log_metric('gini-train', gini(y_true_train, y_pred_train))

        mlflow.catboost.log_model(
            cb_model=clf,
            artifact_path="model")

        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(test_data)
        shap.summary_plot(shap_values, test_data, plot_type="bar", show=False)

        plt.savefig("shap.png")

        mlflow.log_artifact('shap.png')

        ###
        mlflow.log_param('catboost param', params)
        mlflow.log_param('dataset shape', df.shape)


        ##
        print(mlflow.get_artifact_uri())


        ###
        run = mlflow.active_run()
        print("Active run_id: {}".format(run.info.run_id))


run(pd.read_csv('uploads/tcs04_example3k.csv'))