import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
import logging 
import sys
from datetime import datetime
from nordpool_webscraper import *

load_dotenv()

logging.basicConfig(filename="webscraper.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 

logger=logging.getLogger() 
logger.setLevel(logging.WARNING)
consoleHandler = logging.StreamHandler(sys.stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

TOPIC_NAME = "db-ingestion"

def on_connect(client, userdata, flags, rc):
    logger.info(f">> Trying to connect to MQTT broker")
    if rc == 0:
        logger.info(f">> Connected to MQTT broker on topic {TOPIC_NAME}")
        client.subscribe(TOPIC_NAME)
    else:
        logger.error(f">> Connection to MQTT broker failed with code {rc}", exc_info=True)
        sys.exit("Could not connect to MQTT broker") 

def setup_client():
    client = mqtt.Client()
    client.on_connect = on_connect

    # Set your MQTT broker address, port, username, and password
    broker_address = os.getenv('MQTT_IP')
    broker_port = 1883

    client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PW'))
    client.connect(broker_address, broker_port, 60)
    return client

def main():
  try: 
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    logger.info(f">> Successfully fetched energy spot price data.")
  except Exception as e:
    logger.error(f">> Could not fetch energy spot price data due to error - {e}")
    sys.exit("Could not fetch energy spot price data") 

  client = setup_client()
  logger.info(f">> Sending energy spot price to {TOPIC_NAME} topic.")
  client.publish(TOPIC_NAME,payload=json.dumps(msg))

if __name__ == "__main__":
    main()