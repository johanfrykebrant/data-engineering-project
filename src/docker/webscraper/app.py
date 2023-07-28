from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv
import logging 
from sys import stdout
from nordpool_webscraper import *

load_dotenv()

logging.basicConfig(filename="webscraper.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

def on_send_success(record_metadata):
    logger.info(f">> Succesfully produced message to topic {record_metadata.topic}, partition {record_metadata.partition}, with offset {record_metadata.offset}")

def on_send_error(excp):
    logger.error('>> Error when producing message.', exc_info=excp)

def main():
  topic = 'db-ingestion'

  logger.info(f">> Starting producer.")
  producer = KafkaProducer(bootstrap_servers=f"{os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}"
                          ,retries=5
                          ,linger_ms=10)

  try: 
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    msg_byte = json.dumps(msg).encode('utf-8')
    logger.info(f">> Successfully fetched energy spot price data.")
  except Exception as e:
    logger.error(f">> Could not fetch energy spot price data due to error - {e}")

  logger.info(f">> Sending energy spot price to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)

  producer.flush()
  logger.info(f">> Closing producer.")
  producer.close()

if __name__ == "__main__":
    main()