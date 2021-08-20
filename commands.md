# приконектиться к контейнеру
docker exec -it CONTAINTER_ID bash

# собрать образ из текущей папочки
docker build .

# Про билд контейнера
https://git.do.x5.ru/aleksey.podkidyshev/scoringapi/container_registry

docker login registry.do.x5.ru
docker build -t registry.do.x5.ru/aleksey.podkidyshev/scoringapi .
docker push registry.do.x5.ru/aleksey.podkidyshev/scoringapi

docker pull registry.do.x5.ru/aleksey.podkidyshev/scoringapi:a1f2ecc3

# бага с mlflow (если говорит что не может с experiment_id найти переменную)
mlflow experiments create -n 0

# запуск mlflow UI
mlflow ui --host 0.0.0.0 --port 5003

# cleaning
docker system prune


# TODO

# - early_stopping в catboost, чтобы не было по 1k итераций, он явно быстрее сходиться

# - nginx. reversed proxy server.
# См вот тут: https://github.com/sachua/mlflow-docker-compose (крутой проект)

# - подружить optuna с mlflow

# - прочитать про аналогичные REST проекты
# NGINX + FLASK: https://towardsdatascience.com/how-to-deploy-ml-models-using-flask-gunicorn-nginx-docker-9b32055b3d0
# https://towardsdatascience.com/machine-learning-prediction-in-real-time-using-docker-and-python-rest-apis-with-flask-4235aa2395eb
# https://towardsdatascience.com/build-and-run-a-docker-container-for-your-machine-learning-model-60209c2d7a7f