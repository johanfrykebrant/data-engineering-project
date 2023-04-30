# Overview

![This is an image](doc/arcitechture.png)

# Prerequisites

docker
docker compose

# Set up

# .env file
.env-file in the build directory

´´´
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

´´´
## Docker

## DBT
postgres depend.
sudo apt install postgresql libpq-dev postgresql-client
postgresql-client-common -y
pip install dbt-postgres

add .dbt/profiles.yml to home dir.

dbt run --profiles-dir ./profiles.yml
dbt debug --config-dir
´´´
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
´´´
dbt run --full-refresh


## Temperature sensor

  ´´´pip install kafka-python´´´
  ´´´pip install python-dotenv´´´

  transfer files setup cron
  ´´´scp -r temperature-sensor pi@pi-node:/home/pi/temperature-sensor´´´


  ´´´crontab -e´´´
  ´´´0 * * * * python data-engineering-project/src/temperature-sensor/temp-sens-producer.py´´´

  