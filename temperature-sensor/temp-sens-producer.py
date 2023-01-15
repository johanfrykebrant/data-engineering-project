import os
import glob
import time
import socket
from datetime import datetime
import logging 
import json
from dotenv import load_dotenv
from kafka import KafkaProducer

logging.basicConfig(filename="std.log", 
                    format='%(asctime)s | %(message)s', 
                    filemode='w') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
BASE_DIR = '/sys/bus/w1/devices/'
SENSORS = glob.glob('/sys/bus/w1/devices/' + '28*')

def find_sensors():      
    device_files = []
    if len(SENSORS) == 0:
        raise Exception("Unable to read temperature. No sensor found.")
    else:
        for i in range(len(SENSORS)):
            device_files.append(glob.glob(BASE_DIR + '28*')[i] + '/w1_slave')
    return device_files

def read_sens_lines():
    lines = []
    device_files = find_sensors()
    
    for i in range(len(device_files)):
        f = open(device_files[i], 'r')
        lines.append(f.readlines())
        f.close()
    
    return lines
    
def read_temp():
    result_dict = {
                    'destination_schema': 'staging',
                    'destination_table': 'observations',
                    'data': []
    }
    lines = read_sens_lines()

    for line in lines:
        while line[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_sens_lines()

    for i, line in lines:     
        equals_pos = line.find('t=')
        if equals_pos != -1:
            value = float(line[equals_pos+2:]) / 1000.0

            temp_dict = {
                    'observation_name':'Lufttemperatur',
                    'observation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'observation_value': value,
                    'observation_station': socket.gethostname(),
                    'observation_unit': 'degC'
                }
            result_dict["data"].append(temp_dict)  
        else:
            raise Exception("Sensors found but unable to read value.")
       
    return result_dict

def main():
    load_dotenv()
    # create kafka produer
    producer = KafkaProducer(bootstrap_servers=f"{os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}")
    # get temperature reading
    logger.debug(f"{datetime.now()} - Reading from temperature sensor...")
    msg = read_temp()
    # encode forecast data to byte array
    msg_byte = json.dumps(msg).encode('utf-8')
    # send message to kafka topic
    logger.debug(f"{datetime.now()} - Send temperature measurements to db-ingestion topic...")
    print(json.dumps(msg, indent=4))
    producer.send('db-ingestion', msg_byte)
    # close producer
    producer.close()    
    
if __name__ == "__main__":
    main()