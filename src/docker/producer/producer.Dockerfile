FROM alpine:latest

# Install python & pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
COPY src/docker/producer/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Copy necessary files
COPY src/docker/producer/nordpool_webscraper.py root/nordpool_webscraper.py
COPY src/docker/producer/smhi_api.py root/smhi_api.py
COPY src/docker/producer/producer.py root/app.py
COPY build/.env ./.env

# copy crontabs for root user
COPY src/docker/producer/cronjobs /etc/crontabs/root
CMD ["crond","-f", "-d", "1", "-L", "/dev/stdout"]
# Use this when debuging
#CMD ["python3", "root/app.py"]