from csv import reader
import os
import glob
import time
from datetime import datetime

class Reader():

    def __init__(self):
        os.system('sudo modprobe w1-gpio')
        os.system('sudo modprobe w1-therm')
         
        self.device_files = []
        base_dir = '/sys/bus/w1/devices/'
        self.sensors = glob.glob(base_dir + '28*')


        if len(self.sensors) == 0:
            raise Exception("Unable to read temperature. No sensor found.")
        else:
            for i in range(len(self.sensors)):
                self.device_files.append(glob.glob(base_dir + '28*')[i] + '/w1_slave')

    def read_sens_lines(self):
        self.lines = []
        for i in range(len(self.device_files)):
            f = open(self.device_files[i], 'r')
            self.lines.append(f.readlines())
            f.close()
     
    def read_temp(self):
        result_dict = {"Sensor values" : []}
        self.read_sens_lines()
        
        for i in range(len(self.lines)):
            line = self.lines[i]
            s = ''.join( [n for n in self.sensors[i] if n.isdigit()] )
            temp_dict ={ 
              "name" : "Temperature sensor #" +s[-3:],
              "timestamp" : None,
              "value" : None,
              "unit" : "degC"
              }
            
            while line[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                self.read_sens_lines()
            
            equals_pos = line[1].find('t=')
            if equals_pos != -1:
                temp_dict["value"] = float(line[1][equals_pos+2:]) / 1000.0
            else:
                raise Exception("Sensors found but unable to read value.")

            temp_dict["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result_dict["Sensor values"].append(temp_dict)    
            
        return result_dict

def main():
    s = reader()
    t = s.read_temp()
    print(t)
    
if __name__ == "__main__":
    main()