FROM python:3.7-slim-stretch

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile* /app/

RUN pipenv install --system --keep-outdated

ADD . /app

ENV PATH="/app:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"
