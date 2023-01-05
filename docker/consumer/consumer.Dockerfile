FROM python:3.8.3-slim 

COPY consumer/requirements.txt ./requirements.txt
COPY consumer/consumer.py ./app.py
COPY .env ./.env

RUN pip install -r requirements.txt

CMD ["python", "./app.py"]