FROM python:3.8-slim

WORKDIR /Users/aleksejpodkidysev/PycharmProjects/ScoringAPI

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apt-get update \
    &&  apt-get install -y --reinstall build-essential \
    &&  apt-get install -y git

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++\
    && rm -rf /var/lib/apt/lists/* \
    && pip install shap flask\
    && apt-get purge -y --auto-remove gcc g++

RUN pip install -r requirements.txt