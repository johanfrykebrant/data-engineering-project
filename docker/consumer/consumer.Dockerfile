#FROM python:3.8.3-slim 
FROM alpine:latest

# RUN apk update
# RUN apk add libpq-dev gcc
# RUN pip install psycopg2

# RUN apt-get update
# RUN apt-get -y install libpq-dev gcc
# RUN pip install psycopg2

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add libpq-dev gcc
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY consumer/requirements.txt ./requirements.txt
COPY consumer/consumer.py ./app.py
COPY .env ./.env

RUN pip3 install -r requirements.txt

CMD ["python", "./app.py"]