from sklearn.feature_selection import SelectFromModel
from typing import List


def find_best_point(scores: List[float]):
    '''функция которая ищет точку в которой нужно делать разбиение'''
    return 50


def do_select(model, train_pool, test_pool):
    selector = SelectFromModel(estimator=model)

    selector = selector.fit(train_pool, test_pool)
    transformed_train_data = selector.transform(train_data)
    transformed_test_data = selector.transform(test_data)

