from kafka import KafkaConsumer
import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
import logging 

logging.basicConfig(filename="std.log", 
                    format='%(asctime)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)

def write_to_db(data):
    # connect to db
    conn = psycopg2.connect(dbname=os.getenv('DATABASE'),
                            user=os.getenv('DBUSER'),
                            password=os.getenv('PASSWORD'),
                            host=os.getenv('POSTGRES_IP'),
                            port=os.getenv('POSTGRES_PORT'))

    cur = conn.cursor()
    
    schema = data['destination_schema']
    table = data['destination_table']

    data_set = data['data']
    cols=tuple(data_set[0].keys())
    vals_str_list = ["%s"] * len(cols)
    vals_str = ", ".join(vals_str_list)

    vals_list = []
    for data_row in data_set:
        vals_list.append(tuple(data_row.values()))
    # create sql querry string
    querry_str = "INSERT INTO {scehma}.{table} {cols} VALUES ({vals_str})".format(
                cols = cols, vals_str = vals_str,scehma = schema, table = table).replace("'","") 
    
    # execute querry
    cur.executemany(querry_str, vals_list)

    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()

def main():
    load_dotenv()
    # test db connection
    logger.debug(f"{datetime.now()} - Testing database connection")
    conn = psycopg2.connect(dbname=os.getenv('DATABASE'),
                            user=os.getenv('DBUSER'),
                            password=os.getenv('PASSWORD'),
                            host=os.getenv('POSTGRES_IP'),
                            port=os.getenv('POSTGRES_PORT'))

    cur = conn.cursor()
    cur.close()
    topic = 'db-ingestion'
    logger.debug(f"{datetime.now()} - Subscribing to topic {topic} at {os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}")
    
    # subscribe to kafka topic
    consumer = KafkaConsumer(bootstrap_servers=f"{os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}",
                                auto_offset_reset='latest',
                                consumer_timeout_ms=1000)
    consumer.subscribe([topic])

    while True:
        for message in consumer:
            logger.debug(f"{datetime.now()} - Consuming message.")
            # decode bytearray to string and load string as json-obj.
            jobj = json.loads((message.value).decode("utf-8"))
            # write the 
            logger.debug(f"{datetime.now()} - Writing to database.")
            write_to_db(jobj)
    logger.debug(f"{datetime.now()} - Closing database connection")
    consumer.close()

if __name__ == "__main__":
    main()