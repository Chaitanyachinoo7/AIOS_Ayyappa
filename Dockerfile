FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir pipenv

COPY Pipfile /app/Pipfile
RUN PIPENV_VENV_IN_PROJECT=0 pipenv install --system --skip-lock

COPY app /app/app

