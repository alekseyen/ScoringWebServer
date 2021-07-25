FROM python:3.8-slim

WORKDIR /Users/aleksejpodkidysev/PycharmProjects/ScoringAPI

COPY . .

RUN apt-get update \
    &&  apt-get install -y --reinstall build-essential \
    &&  apt-get install -y git

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++\
    && rm -rf /var/lib/apt/lists/* \
    && pip install shap\
    && apt-get purge -y --auto-remove gcc g++

RUN pip install -r requirements.txt