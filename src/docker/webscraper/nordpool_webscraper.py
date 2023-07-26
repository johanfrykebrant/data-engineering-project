from datetime import datetime
import time
import json
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
logger.setLevel(logging.WARNING)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
logger.addHandler(consoleHandler)

NORDPOOL_URL = "https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE/Hourly/?view=table"

def setup_webdriver():
    # Set the path to the chromedriver executable
    chromedriver_path = "/usr/lib/chromium/chromedriver"

    # Set the options for the Chrome webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security restrictions
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

    # Set the path to the Chrome binary (in Alpine, it's located at /usr/bin/chromium-browser)
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    # Create a new instance of the Chrome webdriver
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    #driver = webdriver.Chrome(service=Service(), options=chrome_options)
    return driver

def extract_data_row(row):
    values = row.split(" ")
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

        # Wait to avoid StaleElementReferenceException
        time.sleep(1)
        data_table = WebDriverWait(driver, 3).until(
           EC.visibility_of_element_located((By.ID, "datatable"))
        )

        table_rows = data_table.text.split("\n")

        # Extract date and column names
        date = format_date(table_rows[0])

        data_list = []
        
        for row in table_rows[2:]:

            hour, values = extract_data_row(row)
            # Break loop if hour is None
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
    finally:
        driver.quit()

    return result_dict

def main():
    driver = setup_webdriver()
    msg = get_energy_prices(driver)
    logger.info(f">> Result: {json.dumps(msg, indent=4)}")

if __name__ == '__main__':
    main()