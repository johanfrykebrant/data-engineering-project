# Overview

![This is an image](doc/arcitechture.png)

# Prerequisites

- docker
- docker compose
- a ds18b20 sensor

# Set up

# .env file
.env-file in the build directory

```env
DBUSER = 'xxxxxxx'
DATABASE = 'xxxxxxx'
PASSWORD = 'xxxxxxx'
POSTGRES_IP = 'xxxxxxx'
MQTT_USER = 'xxxxxxx'
MQTT_PW = 'xxxxxxx'
MQTT_IP = 'xxxxxxx'
```

## Docker

## MQTT

# login interactively into the mqtt container
sudo docker exec -it <container-id> sh

# add user and it will prompt for password
mosquitto_passwd -c /mosquitto/config/pwfile user1

sudo docker restart <container-id>


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
  