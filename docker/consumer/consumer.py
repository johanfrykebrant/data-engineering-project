from kafka import KafkaConsumer
import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
import logging 
from sys import stdout

# Get environment variables from .env-file
load_dotenv()

# Config logger
logging.basicConfig(filename="consumer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

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
        logger.error(f">> Failed to write to to database due to error - {e}")
    finally:
        conn.commit()
        cur.close()

def connect_to_db():
    logger.info(f">> Trying to connect to postgres://{os.getenv('DBUSER')}:{os.getenv('PASSWORD')}@{os.getenv('POSTGRES_IP')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('DATABASE')}")       
    conn = None
    try:
        conn = psycopg2.connect(dbname=os.getenv('DATABASE'),
                                user=os.getenv('DBUSER'),
                                password=os.getenv('PASSWORD'),
                                host=os.getenv('POSTGRES_IP'),
                                port=os.getenv('POSTGRES_PORT'))
        logger.info(f">> Successfully connected to postgres://{os.getenv('DBUSER')}:{os.getenv('PASSWORD')}@{os.getenv('POSTGRES_IP')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('DATABASE')}")       
    except Exception as e:
        logger.error(f">> Failed to connect to database due to error - {e}")
    return conn

def create_consumer(topic):
    logger.info(f">> Creating consumer, bootstrapserver = {os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}, topic = {topic}")
    consumer = KafkaConsumer(topic,
                            bootstrap_servers=f"{os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}",
                            auto_offset_reset='latest',
                            )
    return consumer

def main():
    
    logger.info(f">> Testing databse connection")
    try:
        conn = connect_to_db()
        conn.close()
        logger.info(f">> Succesfully connected to database.")
    except:
        logger.error(f">> Could not connect ot databse.")
    
    topic = 'db-ingestion'
    consumer = create_consumer(topic)
    
    try:
        for message in consumer:
            logger.info(f">> Consuming message from topic {message.topic}, partition {message.partition}, with offset {message.offset}")
            # Decode bytearray to string and load string as json-obj.
            jobj = json.loads((message.value).decode("utf-8"))
            # Write the message to db
            conn = connect_to_db()
            write_to_db(conn,jobj)
            conn.close()
    except Exception as e:
        logger.error(f">> Failed to consume message from topic {topic} to database due to error - {e}")
    finally:
        logger.info(f">>  Shutting down consumer.")
        consumer.close()
 

if __name__ == "__main__":
    main()