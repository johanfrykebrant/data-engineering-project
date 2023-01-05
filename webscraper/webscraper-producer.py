from flask import Flask
from flask_restful import Api
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import json

def get_energy_prices():
    # Setting up webdriver
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage') # Not used 
   
    url = "https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/SE/Hourly/?view=table"
    driver = webdriver.Chrome(options=options)
    driver.get(url)

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

    # collecting data
    for row in table_rows:
        values = row.text.split(" ")[2:]
        hr = values[0]
        timestamp = date + " " + hr + ":00"
        timestamps.append(timestamp) 
        se1.append(float(values[1].replace(",",".")))
        se2.append(float(values[2].replace(",",".")))
        se3.append(float(values[3].replace(",",".")))
        se4.append(float(values[4].replace(",",".")))

    # create dataframe
    data = {'SE1' :  se1,
            'SE2' :  se2,
            'SE3' :  se3,
            'SE4' :  se4}
    df = pd.DataFrame(data, columns=col_names[1:], index=timestamps)

    # turn the df into a json object
    data_json = df.to_json(orient="table")
    parsed = json.loads(data_json)
    result = json.dumps(parsed, indent=4)

    # quiting driver
    driver.quit()

    return result


app = Flask(__name__)
api = Api(app)


@app.route('/day_ahead', methods=['GET'])
def get():
    return get_energy_prices()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=9007)