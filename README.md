# Overview

![This is an image](doc/arcitechture.png)

# Prerequisites

dbt-postgres
dbt-core
docker
docker compuse

# Set up

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

dbt run --profiles-dir /home/paddan/source/data-engineering-project/dbt_proj



conn = psycopg2.connect(dbname='',user='user',password='password123',host='192.168.1.101',port='5432')
  