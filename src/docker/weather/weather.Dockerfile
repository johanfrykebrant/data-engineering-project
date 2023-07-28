FROM alpine:latest

# Install python & pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
COPY src/docker/weather/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Copy necessary files
COPY src/docker/weather/smhi_api.py root/smhi_api.py
COPY src/docker/weather/app.py root/app.py
COPY build/.env ./.env

# Copy crontabs for root user
COPY src/docker/weather/cronjobs /etc/crontabs/root
CMD ["crond","-f", "-d", "1", "-L", "/dev/stdout"]
# - '-f': Runs cron in the foreground, printing logs to the terminal.
# - '-d 1': Enables basic debug messages (debug level 1) for easier troubleshooting.
# - '-L /dev/stdout': Redirects cron log messages to the container's stdout, visible via 'docker logs'.