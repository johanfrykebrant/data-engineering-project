# Use Alpine as the base image
FROM alpine:latest

# Install necessary packages
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    wget \
    unzip \
    xvfb \
    curl \
    chromium \
    chromium-chromedriver

# Install Selenium
RUN pip3 install selenium==4.4.3 webdriver_manager
RUN pip3 install kafka-python==2.0.2

# Set up Xvfb (X Virtual Frame Buffer)
RUN Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# Set the environment variables
ENV DISPLAY=:99
ENV PATH="/usr/local/bin:${PATH}"

# Copy application file to the container
COPY src/docker/webscraper/nordpool_webscraper.py root/nordpool_webscraper.py
COPY src/docker/webscraper/app.py root/app.py
COPY build/.env ./.env

# Set up cronjob
COPY src/docker/webscraper/cronjobs /etc/crontabs/root
CMD ["crond","-f", "-d", "1", "-L", "/dev/stdout"]
# - '-f': Runs cron in the foreground, printing logs to the terminal.
# - '-d 1': Enables basic debug messages (debug level 1) for easier troubleshooting.
# - '-L /dev/stdout': Redirects cron log messages to the container's stdout, visible via 'docker logs'.