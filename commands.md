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
docker builder prune
docker system df