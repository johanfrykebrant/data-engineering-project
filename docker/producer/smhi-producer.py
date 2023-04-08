from kafka import KafkaProducer
from socket import gaierror
from urllib3.exceptions import MaxRetryError, NewConnectionError
from requests import get, ConnectionError
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging 
from sys import stdout

load_dotenv()

logging.basicConfig(filename="producer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

NAME_CODES ={
    'msl': 'Air pressure',
    't': 'Air temperature',
    'vis': 'Horizontal visibility',
    'wd': 'Wind direction',
    'ws': 'Wind speed',
    'r': 'Relative humidity',
    'tstm': 'Thunder probability',
    'tcc_mean': 'Mean value of total cloud cover',
    'lcc_mean': 'Mean value of low level cloud cover',
    'mcc_mean': 'Mean value of medium level cloud cover',
    'hcc_mean': 'Mean value of high level',
    'gust': 'Wind gust speed',
    'pmin': 'Minimum precipitation intensity',
    'pmax': 'Maximum precipitation intensity',
    'spp': 'Percent of precipitation in frozen form',
    'pcat': 'Precipitation category',
    'pmean': 'Mean precipitation intensity',
    'pmedian': 'Median precipitation intensity',
    'Wsymb2': 'Weather symbol',
    }

def get_observations(station_number):
    """
    Fetch weather observation from weather station given as input to the function using SMHI's open API.
    See available weather stations at https://www.smhi.se/polopoly_fs/1.2874!rrm6190%5B1%5D.pdf.
    See API documentation at https://opendata.smhi.se/apidocs/metobs
    """
    SMHI_OBSERVATION = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/<parameter>/station/"+ str(station_number) + "/period/latest-hour/data.json"
    result_dict = []
    parameters = [1,3,4,6,7,21,25]
    result_dict = {
                'destination_schema': 'staging',
                'destination_table': 'observations',
                'data': []
    }
    def epoch_to_date(epoch_datetime):
        dateStr = datetime.fromtimestamp(epoch_datetime/1000).strftime('%Y-%m-%d %H:%M:%S')
        return dateStr

    for param in parameters:
        
        logger.info(f">> Requesting observations for parameter number {param}")
        url = SMHI_OBSERVATION.replace("<parameter>",str(param))
        try:
            r = get(url)
        except (ConnectionError, NewConnectionError, gaierror, MaxRetryError):
            logger.critical("Failed GET request. Could not establish connection. Ensure that device has internet acecss")
            return None
        
        jobj = r.json()
        logger.info(f">> {r.request.method} request from {r.url} returned <Response{r.status_code}>") 
        values = jobj["value"]
        
        if r.status_code == 200:
            if values != None:
              for value in values:
                temp_dict ={
                    'observation_name':jobj["parameter"]["name"],
                    'observation_timestamp':epoch_to_date(value['date']),
                    'observation_value':value["value"],
                    'observation_station':jobj["station"]["name"],
                    'observation_unit':jobj["parameter"]["unit"]
                }
                result_dict['data'].append(temp_dict)
        else:
          logger.error(f">> {r.request.method} request from {r.url} was not succsessfull")
    return result_dict

def get_forecasts(longitude,latitude):
    """
    Fetch forecast for weatherstation closest to the given longitude and latitude using SMHI's open API.
    See API documentation at https://opendata.smhi.se/apidocs/metfcst
    """
    SMHI_FORECAST = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/" + longitude + "/lat/" + latitude + "/data.json"
    
    def date_str_format(string):
      dateStr = string.replace('T',' ').replace('Z','').replace('"','')
      return dateStr
    
    try:
      r = get(SMHI_FORECAST)
    except (ConnectionError, NewConnectionError, gaierror, MaxRetryError):
      logger.critical(">> Failed GET request. Could not establish connection. Ensure that device has internet acecss")
      return None

    result_dict = {
                    'destination_schema': 'staging',
                    'destination_table': 'forecasts',
                    'data': None
    }
    logger.info(f">> {r.request.method} request from {r.url} returned <Response{r.status_code}>") 
    if r.status_code == 200:
  
      jobj = r.json()

      approved_timestamp = date_str_format(json.dumps(jobj["approvedTime"]))
      coordinates = tuple(jobj["geometry"]["coordinates"][0])
      forecasts = jobj["timeSeries"]
      data_list = []
      for forecast in forecasts:
        time = date_str_format(json.dumps(forecast["validTime"]))
        for i in forecast["parameters"]:
          temp_dict ={ 
            "forecast_code" : i["name"],
            "forecast_approved_timestamp": approved_timestamp,
            "forecast_timestamp": time,
            "forecast_coordinates": coordinates,
            "forecast_unit" : i["unit"],
            "forecast_value" : i["values"][0]
            }
          data_list.append(temp_dict)
        result_dict['data'] = data_list
    else:
      logger.error(f">> {r.request.method} request from {r.url} was not succsessfull")
      return None
    return result_dict

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

  msg = get_forecasts(longitude = '13.07',latitude = '55.6')
  # encode forecast data to byte array
  msg_byte = json.dumps(msg).encode('utf-8')

  logger.info(f">> Sending forecasts to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)

  station_number = 52350
  msg = get_observations(station_number)
  # encode observation data to byte array
  msg_byte = json.dumps(msg).encode('utf-8')

  logger.info(f">> Sending observations to {topic} topic.")
  producer.send(topic, msg_byte).add_callback(on_send_success).add_errback(on_send_error)
  
  producer.flush()
  logger.info(f">> Closing producer.")
  producer.close()

if __name__ == "__main__":
    main()