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

# Install Selenium and its requirements
RUN pip3 install selenium==4.4.3 webdriver_manager

# Set up Xvfb (X Virtual Frame Buffer)
RUN Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# Set the environment variables
ENV DISPLAY=:99
ENV PATH="/usr/local/bin:${PATH}"

# Copy application file to the container
COPY src/docker/webscraper/nordpool_webscraper.py root/app.py

CMD ["python3", "root/app.py"]