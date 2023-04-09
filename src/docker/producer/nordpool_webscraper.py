from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import json
import os
import logging
from sys import stdout
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()

logging.basicConfig(filename="producer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

NORDPOOL_URL = "https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE/Hourly/?view=table"

def setup_webdriver():
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("window-size=1920x1080")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')

        driver = webdriver.Remote(command_executor=f"http://{os.getenv('SELENIUM_IP')}:{os.getenv('SELENIUM_PORT')}/wd/hub",
                                options=options
                                )
    except Exception as e:
        logger.error(f">> Failed to create webdriver due to error - {e}")
    return driver

def get_energy_prices(driver):
    if driver is None:
        raise ValueError('Driver is None. Please pass a valid webdriver object.')
    
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
        logger.error(f">> Failed to scrape data from url {NORDPOOL_URL} due to error - {e}")
    finally:
        driver.quit()

    return result_dict

def main():
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    print(json.dumps(msg, indent=4))

if __name__ == '__main__':
    main()