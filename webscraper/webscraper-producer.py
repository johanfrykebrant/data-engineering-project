from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import json
import os
from dotenv import load_dotenv
from kafka import KafkaProducer

NORDPOOL_URL = "https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE/Hourly/?view=table"

def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    # ta bort dessa
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--disable-dev-shm-usage') # Not used 
    
    driver = webdriver.Remote(command_executor=f"http://:{os.getenv('SELENIUM_IP')}:{os.getenv('SELENIUM_PORT')}/wd/hub",
                            options=options
                            )
    return driver


def get_energy_prices():
   
    driver = setup_webdriver()
    driver.get(NORDPOOL_URL)

    result_dict = {
                    'destination_schema': 'staging',
                    'destination_table': 'energy_prices',
                    'data': []
                }
    try:
        # Wait to aviod buggy response
        time.sleep(1)

        # Change currency from EUR to SEK
        xpath = "/html/body/div[@id='page']/div[@id='main']/div/div[@class='pure-g ng-scope']/div[@id='dashboard-column']/div[@class='column']/div[@class='dashboard-box']/div[@class='dashboard-controls']/div[@class='dashboard-control-padding']/div[@class='dashboard-control dashboard-indent']/div[@class='pure-form pure-form-inline date-form ng-scope']/div[@class='dashboard-control-dropdown-wrapper ng-scope']/select[@id='data-currency-select']"
        dropdown = Select(driver.find_element_by_xpath(xpath))
        dropdown.select_by_visible_text("SEK")

        # Wait to aviod buggy response
        time.sleep(1)

        # get all the <tr> items in the driver 
        tr_items = driver.find_elements_by_tag_name('tr')
        table_rows = tr_items[9:-8]  # filter out the ones that are not part of the table

        # get  column names and date
        tmp_list = tr_items[8].text.split("\n")
        date = tmp_list[0].split("-")
        date.reverse()
        date = "-".join(date)

        col_names = tmp_list[1].split(" ")
        col_names.insert(0,'TIMESTAMP')

        timestamps = []
        se1 = []
        se2 = []
        se3 = []
        se4 = []

        # format values
        def format_values(value):
            # If value can not be formated to float, return null.
            try:
                return float(value.replace(",","."))
            except:
                return None

        # collecting timestamps and values in lists
        for row in table_rows:
            values = row.text.split(" ")[2:]
            hr = values[0]
            timestamp = date + " " + hr + ":00"
            timestamps.append(timestamp) 
            se1.append(format_values(values[1]))
            se2.append(format_values(values[2]))
            se3.append(format_values(values[3]))
            se4.append(format_values(values[4]))

        data_list = []
        for i in range(len(timestamps)):
            temp_dict ={ 
            "price_timestamp":  timestamps[i],
            "price":  se1[i],
            "bidding_zone":  'se1',
            "unit" : 'Sek/kWh',
            }
            data_list.append(temp_dict)
            temp_dict ={ 
            "price_timestamp":  timestamps[i],
            "price":  se2[i],
            "bidding_zone":  'se2',
            "unit" : 'Sek/kWh',
            }
            data_list.append(temp_dict)
            temp_dict ={ 
            "price_timestamp":  timestamps[i],
            "price":  se3[i],
            "bidding_zone":  'se3',
            "unit" : 'Sek/kWh',
            }
            data_list.append(temp_dict)
            temp_dict ={ 
            "price_timestamp":  timestamps[i],
            "price":  se4[i],
            "bidding_zone":  'se4',
            "unit" : 'Sek/kWh',
            }
            data_list.append(temp_dict)

        result_dict['data'] = data_list
    except Exception as e:
        print(e)
    finally:
        driver.quit()

    return result_dict

def main():
  load_dotenv()
  # create produer
  producer = KafkaProducer(bootstrap_servers=f"{os.getenv('KAFKA_IP')}:{os.getenv('KAFKA_PORT')}")
  # get forecast data
  print('fetching energy prices...')
  msg = get_energy_prices()
  
  #print(json.dumps(msg, indent=4))
  # encode forecast data to byte array
  msg_byte = json.dumps(msg).encode('utf-8')
  # send message to kafka topic
  print('sending message to kafka topic...')
  producer.send('db-ingestion', msg_byte)

if __name__ == '__main__':
    main()