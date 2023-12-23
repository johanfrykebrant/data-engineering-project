import paho.mqtt.client as mqtt
import psycopg2
from dotenv import load_dotenv
import logging
from sys import stdout
import os
import json

# Configure logging
logging.basicConfig(filename="consumer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

TOPIC_NAME = "hello/topic"
load_dotenv()

# Initialize the database connection pool
def connect_to_database():
    logger.info(f">> Trying to connect to postgres://{os.getenv('DBUSER')}:<password>@{os.getenv('POSTGRES_IP')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('DATABASE')}")       
    conn = None
    try:
        conn = psycopg2.connect(dbname=os.getenv('DATABASE'),
                                user=os.getenv('DBUSER'),
                                password=os.getenv('PASSWORD'),
                                host=os.getenv('POSTGRES_IP'),
                                port=os.getenv('POSTGRES_PORT'))
        logger.info(f">> Successfully connected to postgres://{os.getenv('DBUSER')}:<password>@{os.getenv('POSTGRES_IP')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('DATABASE')}")       
    except Exception as e:
        logger.error(f">> Failed to connect to database due to error - {e}", exc_info=True)
    return conn

def build_querry_string(data):
    schema = data['destination_schema']
    table = data['destination_table']

    data_set = data['data']
    cols=tuple(data_set[0].keys())
    vals_str_list = ["%s"] * len(cols)
    vals_str = ", ".join(vals_str_list)

    values_list = []
    for data_row in data_set:
        values_list.append(tuple(data_row.values()))

    querry_str = "INSERT INTO {scehma}.{table} {cols} VALUES ({vals_str})".format(
                cols = cols, vals_str = vals_str,scehma = schema, table = table).replace("'","") 
    
    return querry_str,values_list

def write_to_db(conn,data):
    try:
        cur = conn.cursor()
        querry_str, values_list = build_querry_string(data)
        cur.executemany(querry_str, values_list)
        logger.info(f">> Inserting {len(values_list)} rows to {data['destination_schema']}.{data['destination_table']}")
    except Exception as e:
        logger.error(f">> Failed to write to to database due to error - {e}", exc_info=True)
    finally:
        conn.commit()
        cur.close()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f">> Connected to MQTT broker")
        client.subscribe(TOPIC_NAME)
    else:
        logger.error(f">> Connection to MQTT broker failed with code {rc}")

def on_message(client, userdata, msg):
    logger.info(f">> Received message: {msg.payload} on topic: {msg.topic}")
    conn = connect_to_database()
    jobj = json.loads((msg.payload).decode("utf-8"))
    print(jobj)
    write_to_db(conn,jobj)
    conn.close()

def setup_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Set your MQTT broker address, port, username, and password
    broker_address = os.getenv('MQTT_IP')
    broker_port = 1883

    client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PW'))
    client.connect(broker_address, broker_port, 60)
    return client

def main():
    client = setup_client()
    while True:
        client.loop()

if __name__ == "__main__":
    main()