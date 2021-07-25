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

from enum import Enum


class LearningType(Enum):
    SINGLE = 'single'
    RANDOMIZED = 'randomized'
    GRID = 'grid'


CAT_FEATURES = ['region_x5', 'region_rossvyaz', 'loyalty_appl_form_status_code',
                'loyalty_card_status_dk', 'loyalty_card_type_code', 'gender_dk']
DEFAULT_PARAMS = {
    'depth': 6,
    'learning_rate': 0.15,
    'iterations': 200}

DEFAULT_GRID_SEARCH = {
    'learning_rate': [0.03, 0.1],
    'depth': [4, 6, 10],
    'l2_leaf_reg': [1, 3, 5, 7, 9]}

gini = lambda y_true, y_pred: 2 * roc_auc_score(y_true, y_pred) - 1


def do_actual_cat_features(df):
    ans = []
    for feat in df.columns:
        if feat in CAT_FEATURES:
            df[feat] = df[feat].astype(str)
            ans.append(feat)

    return ans


def run(df: pd.DataFrame,
        params: Dict = DEFAULT_PARAMS,
        search_type: LearningType = LearningType.SINGLE):
    cat_features = do_actual_cat_features(df)
    train, test = train_test_split(df, test_size=0.25)

    train_data = Pool(data=train.drop(columns=['target']),
                      label=train.target.astype(int),
                      cat_features=cat_features)

    test_data = Pool(data=test.drop(columns=['target']),
                     cat_features=cat_features)

    clf = CatBoostClassifier(
        eval_metric='AUC:hints=skip_train~false',
        loss_function='Logloss',
    )

    if search_type == LearningType.GRID:
        params = clf.grid_search(DEFAULT_GRID_SEARCH, train_data, plot=True)['params']
    if search_type == LearningType.RANDOMIZED:
        params = clf.randomized_search(DEFAULT_GRID_SEARCH, train_data, plot=True)['params']

    clf = CatBoostClassifier(
        **params,
        eval_metric='AUC:hints=skip_train~false',
        loss_function='Logloss',
        early_stopping_rounds=10,
        random_state=13,
    )

    with mlflow.start_run():
        os.mkdir('graphs')
        os.mkdir('datasets')

        train.to_csv('datasets/train_dataset.csv')
        test.to_csv('datasets/test_dataset.csv')

        mlflow.log_artifacts('datasets', artifact_path='datasets')

        print('starting fit')

        clf.fit(train_data, plot=True, verbose=False)

        ############## feature importance csv

        importance_df = pd.DataFrame(
            {'feature': clf.feature_names_, 'importance': clf.get_feature_importance(train_data)})
        importance_df.sort_values(by=['importance'], ascending=False, inplace=True)
        importance_df.to_csv('graphs/importance.csv')

        ############## make predict

        do_actual_cat_features(test)

        y_pred_test = clf.predict_proba(test_data)[:, 1]
        y_true_test = test.target.astype(int)

        y_pred_train = clf.predict_proba(train_data)[:, 1]
        y_true_train = train.target.astype(int)

        ###################

        mlflow.log_metric('roc-auc-test', roc_auc_score(y_true_test, y_pred_test))
        mlflow.log_metric('gini-test', gini(y_true_test, y_pred_test))

        mlflow.log_metric('roc-auc-train', roc_auc_score(y_true_train, y_pred_train))
        mlflow.log_metric('gini-train', gini(y_true_train, y_pred_train))

        mlflow.catboost.log_model(
            cb_model=clf,
            artifact_path="model")

        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(test_data)
        shap.summary_plot(shap_values, test_data, plot_type="bar", show=False,
                          feature_names = test_data.get_feature_names())

        plt.savefig("graphs/shap.png")

        mlflow.log_artifacts('graphs', artifact_path='graphs')

        mlflow.log_param('catboost param', params)
        mlflow.log_param('dataset shape', df.shape)

        ######## delete temp log folders

        shutil.rmtree('graphs')
        shutil.rmtree('datasets')

        run = mlflow.active_run()
        print("Active run_id: {}".format(run.info.run_id))

# run(pd.read_csv('uploads/tcs04_example3k.csv'))
