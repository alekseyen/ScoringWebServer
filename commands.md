docker exec -it CONTAINTER_ID bash// for connect in docker files

mlflow run . -e 'run_model.py' --no-conda

docker build . # to build current Dockerfile

# Про билд контейнера
https://git.do.x5.ru/aleksey.podkidyshev/scoringapi/container_registry

docker login registry.do.x5.ru
docker build -t registry.do.x5.ru/aleksey.podkidyshev/scoringapi .
docker push registry.do.x5.ru/aleksey.podkidyshev/scoringapi

to pull image: docker pull registry.do.x5.ru/aleksey.podkidyshev/scoringapi:a1f2ecc3
(просто нажать эконку скопировать с jupyter hub)