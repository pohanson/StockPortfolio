FROM python:3.12-slim AS data

FROM python:3.12-slim AS base

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src .

CMD ["python", "-u", "main.py"]
