FROM alpine:latest

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY producer/requirements.txt ./requirements.txt
COPY producer/smhi-producer.py ./app.py
COPY .env ./.env

# copy crontabs for root user
COPY producer/cronjobs /etc/crontabs/root

RUN pip3 install -r requirements.txt
CMD ["python", "./app.py"]
#CMD ["crond", "-f", "-d", "8",]
