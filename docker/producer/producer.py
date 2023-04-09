from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv
import logging 
from sys import stdout
from smhi_api import *
from nordpool_webscraper import *

load_dotenv()

logging.basicConfig(filename="producer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)
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
    msg = get_forecasts(longitude = '13.07',latitude = '55.6')
    msg_byte = json.dumps(msg).encode('utf-8')
    logger.info(f">> Successfully fetched weather forecast data.")
  except Exception as e:
    logger.error(f">> Could not fetch weather forecast data due to error - {e}")

  logger.info(f">> Sending forecasts to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)

  try:
    station_number = 52350
    msg = get_observations(station_number)
    msg_byte = json.dumps(msg).encode('utf-8')
    logger.info(f">> Successfully fetched weather observations data.")
  except Exception as e:
    logger.error(f">> Could not fetch weather observations data due to error - {e}")
  
  logger.info(f">> Sending observations to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)

  try:
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    msg_byte = json.dumps(msg).encode('utf-8')
    logger.info(f">> Successfully fetched energy spot prices data.")
  except Exception as e:
    logger.error(f">> Could not fetch energy spot prices data due to error - {e}")
  
  logger.info(f">> Sending energy prices to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)

  producer.flush()
  logger.info(f">> Closing producer.")
  producer.close()

if __name__ == "__main__":
    main()