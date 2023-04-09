FROM python:3.8.3-slim 

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY src/docker/consumer/requirements.txt ./requirements.txt
COPY src/docker/consumer/consumer.py ./app.py
COPY build/.env ./.env

RUN pip install -r requirements.txt

CMD ["python", "./app.py"]