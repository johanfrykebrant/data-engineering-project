from decimal import Decimal
from datetime import datetime
import simplejson as json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import logging
from sys import stdout
from dotenv import load_dotenv
import re
#from kafka import KafkaProducer

load_dotenv()

logging.basicConfig(filename="producer.log", 
                    format='%(asctime)s | %(levelname)s | %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

NORDPOOL_URL = "https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE/Hourly/?view=table"

def setup_webdriver():
    driver = None
    try:
        # Set the path to the chromedriver executable
        #chromedriver_path = "/usr/lib/chromium/chromedriver"

        # Set the options for the Chrome webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security restrictions
        chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

        # Set the path to the Chrome binary (in Alpine, it's located at /usr/bin/chromium-browser)
        #chrome_options.binary_location = "/usr/bin/chromium-browser"

        # Create a new instance of the Chrome webdriver
        #driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        driver = webdriver.Chrome(service=Service(), options=chrome_options)
    except Exception as e:
        logger.error(f">> Failed to create webdriver due to error - {e}")
    return driver

def extract_data_row(row):
    values = row.text.split(" ")
    pattern = re.compile(r'\d{2}')
    if pattern.fullmatch(values[0]):
        return values[0], values[3:]
    return None, [None] * 4

def format_date(date_str):
    date = datetime.strptime(date_str, "%d-%m-%Y")
    return date.strftime("%Y-%m-%d")

def format_values(value):
    # If value can not be formated to float, return null.
    try:
        return float(value.replace(",","."))
    except:
        return None

def get_energy_prices(driver):
    if driver is None:
        raise ValueError('>> Driver is None. Please pass a valid webdriver object.')

    result_dict = {
                    'destination_schema': 'staging',
                    'destination_table': 'energy_prices',
                    'data': []
                }
    try:
        driver.get(NORDPOOL_URL)

        # Wait for currency dropdown to be visible
        dropdown = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, 'data-currency-select'))
        )
        # Change currency from EUR to SEK
        Select(dropdown).select_by_visible_text("SEK")

        # data_table = driver.find_element(By.ID, "datatable")
        # tr_items = data_table.find_elements(By.TAG_NAME,'tr')

        data_table = WebDriverWait(driver, 3).until(
           EC.visibility_of_element_located((By.ID, "datatable"))
        )
        tr_items = WebDriverWait(data_table, 5).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ":scope > tr"))
        )
        
        # extract the table header
        table_header = tr_items[0].text.split("\n")

        # extract date and column names
        date = format_date(table_header[0])

        data_list = []
        
        # collecting timestamps and values in lists
        for row in tr_items[1:]:

            # break loop if first value is not timestamp
            hour, values = extract_data_row(row)
            if hour:
                for i, zone in enumerate(['se1', 'se2', 'se3', 'se4']):
                    temp_dict = {
                        "price_timestamp": f"{date} {hour}:00",
                        "price": format_values(values[i]),
                        "bidding_zone": zone,
                        "unit": "sek/kWh"
                    }
                    data_list.append(temp_dict)
            else:
                break

        result_dict['data'] = data_list
    except Exception as e:
        logger.error(f">> Failed to scrape data from url {NORDPOOL_URL} due to error - {e}")
    finally:
        driver.quit()

    return result_dict

def main():
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    logger.info(f">> Result: {json.dumps(msg, indent=4)}")

if __name__ == '__main__':
    main()