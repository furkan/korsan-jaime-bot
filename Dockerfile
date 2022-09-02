FROM python:3.8

WORKDIR /kjbot

RUN pip install -U pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
