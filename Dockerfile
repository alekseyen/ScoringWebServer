#FROM python:3.8-slim
FROM registry.do.x5.ru/shared/base-containers/python/3.8:2021-04-13-0

WORKDIR /scoringapi

COPY . .

RUN apt-get update \
    &&  apt-get install -y --reinstall build-essential g++\
    &&  apt-get install -y git

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++\
    && rm -rf /var/lib/apt/lists/* \
    && pip install shap flask\
    && apt-get purge -y --auto-remove gcc g++

RUN pip install -r requirements.txt

#CMD rm -r mlruns

#CMD [ "gunicorn", "-b", "0.0.0.0:5000", "main:app", "--reload", "--timeout 1200", "--workers", "4"]