from csv import reader
import os
import glob
import time
from datetime import datetime


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
    result_dict = {"Sensor values" : []}
    lines = read_sens_lines()
    for i in range(len(lines)):
        line = lines[i]
        s = ''.join( [n for n in SENSORS[i] if n.isdigit()] )
        temp_dict ={ 
            "name" : "Temperature sensor #" +s[-3:],
            "timestamp" : None,
            "value" : None,
            "unit" : "degC"
            }
        
        #Oklart vad jag håller på med här... :)
        while line[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_sens_lines()
        
        equals_pos = line[1].find('t=')
        if equals_pos != -1:
            temp_dict["value"] = float(line[1][equals_pos+2:]) / 1000.0
        else:
            raise Exception("Sensors found but unable to read value.")

        temp_dict["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result_dict["Sensor values"].append(temp_dict)    
        
    return result_dict

def main():
    t = read_temp()
    print(t)
    
if __name__ == "__main__":
    main()