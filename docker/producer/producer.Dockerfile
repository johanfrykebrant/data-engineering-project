FROM alpine:latest

# Install python & pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
COPY producer/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Copy necessary files
COPY producer/smhi-producer.py root/app.py
COPY .env ./.env

# copy crontabs for root user
COPY producer/cronjobs /etc/crontabs/root
CMD ["crond","-f", "-d", "1", "-L", "/dev/stdout"]