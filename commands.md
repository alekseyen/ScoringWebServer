docker exec -it CONTAINTER_ID bash// for connect in docker files

mlflow run . -e 'run_model.py' --no-conda

# Про билд контейнера
https://git.do.x5.ru/aleksey.podkidyshev/scoringapi/container_registry

docker login registry.do.x5.ru
docker build -t registry.do.x5.ru/aleksey.podkidyshev/scoringapi .
docker push registry.do.x5.ru/aleksey.podkidyshev/scoringapi