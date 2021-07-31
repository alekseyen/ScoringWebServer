import inspect

import pandas as pd
from catboost import CatBoostClassifier
from catboost import Pool
from sklearn import feature_selection

# def sklearn_selector(selector: feature_selection.):


class SklearnSelector:
    """
    Available classes
        GenericUnivariateSelect',
       'SequentialFeatureSelector',
       'RFE',
       'RFECV',
       'SelectFdr',
       'SelectFpr',
       'SelectFwe',
       'SelectKBest',
       'SelectFromModel',
       'SelectPercentile',
       'VarianceThreshold',
       'chi2',
       'f_classif',
       'f_oneway',
       'f_regression',
       'mutual_info_classif',
       'mutual_info_regression',
       'SelectorMixin'
    """

    available_methods = inspect.getmembers(feature_selection, inspect.isclass)

    def __init__(self, method: str = "SelectFromModel", max_features: float = float("inf")):
        self.method = method
        self.selector_class = None
        self.selector = None

        for name, instance in self.available_methods:
            if name == method:
                self.selector_class = instance
        assert self.selector_class is not None

    def fit(self, model: CatBoostClassifier, train: Pool, max_features: int) -> None:
        self.selector = self.selector_class(model, n_features_to_select=max_features, varbose=True)
        self.selector.fit(train)

    def transform(self, train):
        assert self.selector is not None, "use fit first"

        return


print(inspect.getmembers(feature_selection, inspect.isclass))
