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
KAFKA_IP = 'xxxxxxx'
SELENIUM_IP = 'xxxxxxx'
KAFKA_PORT = 'xxxxxxx'
ZOOKEEPER_PORT = 'xxxxxxx'
POSTGRES_PORT = 'xxxxxxx'
SELENIUM_PORT = 'xxxxxxx'
```

## Docker

## DBT
postgres depend.
sudo apt install postgresql libpq-dev postgresql-client
postgresql-client-common -y
pip install dbt-postgres

add .dbt/profiles.yml to home dir.

```bash
dbt run --profiles-dir ./profiles.yml
dbt debug --config-dir
```

```yaml
dbt_proj:
  outputs:
    dev:
      type: postgres
      threads: 1
      host: xxxxxxx
      port: 5432
      user: xxxxxxx
      pass: xxxxxxx
      dbname: xxxxxxx
      schema: staging
  target: dev
```

```bash
dbt run --full-refresh
```

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
  