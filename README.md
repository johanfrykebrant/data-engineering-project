# Overview

![This is an image](doc/arcitechture.png)

# Prerequisites

- docker
- docker compose
- a ds18b20 sensor
- some sort of raspberry pi (I use nano)

# Set up

# .env file
.env-file in the build directory

```env
DBUSER = 'xxxxxxx'
DATABASE = 'xxxxxxx'
PASSWORD = 'xxxxxxx'
POSTGRES_IP = 'xxxxxxx'
KAFKA_IP = 'xxxxxxx'
GRAFANA_IP = 'xxxxxxx'
KAFKA_PORT = 'xxxxxxx'
ZOOKEEPER_PORT = 'xxxxxxx'
POSTGRES_PORT = 'xxxxxxx'
SELENIUM_PORT = 'xxxxxxx'
```

## Docker

## Grafana

## Temperature sensor

```bash
pip install kafka-python
pip install python-dotenv
```

transfer files setup cron
```bash
scp -r temperature-sensor pi@pi-node:/home/pi/temperature-sensor
```

```bash
crontab -e
0 * * * * python temperature-sensor/temp-sens-producer.py
```
  