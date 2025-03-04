from tuppersat.radio.gps2 import GPS
from tuppersat.radio.Temperature import Temperature
from tuppersat.radio.Pressure import Pressure
from lib.SD_CARD import sd_card
import tuppersat.radio._packet_utils
from tuppersat.radio.radio_class import Radio
import time


def setup(sensors):
    for sensor in sensors:
        sensor.setup()
    
def write(sensors_housekeeping, housekeeping_data):
    sensor_data = []
    for sensor in sensors_housekeeping:
        sensor.read_data()
        sensor_data.append(sensor.data)
        
    if sensor_data[0] is not None and sensor_data[0][1] !='':
        print(sensor_data)
        housekeeping_data["hhmmss"]=(sensor_data[0][3])
        housekeeping_data["latitude"]=(float(sensor_data[0][0]))
        housekeeping_data["longitude"]=(float(sensor_data[0][1]))
        housekeeping_data["hdop"] = (float(sensor_data[0][4]))
        housekeeping_data["altitude"]=(float(sensor_data[0][2]))
        housekeeping_data["ext_temp"]=(float(777))
        housekeeping_data["int_temp"]=(float(sensor_data[1]))
        housekeeping_data["Pressure"]=(float(777))
        
    return housekeeping_data

def main():
    ds_pin_ext = 19
    ds_pin_int = 14
    sensors_housekeeping = [GPS(), Temperature(ds_pin_int)] #Pressure() Temperature(ds_pin_ext)
    sd = sd_card()
    housekeeping_data = {"hhmmss":None,"latitude":None,"longitude":None,"altitude":None,"hdop":None,"int_temp":None,"ext_temp":None,"Pressure":None}
    housekeeping_keys = ["hhmmss","latitude","longitude","altitude","hdop","int_temp","ext_temp","Pressure"]
    setup(sensors_housekeeping)
    sd.setup()
    radio = Radio()
    try:
        while True:
            house_data = write(sensors_housekeeping, housekeeping_data)
            #print(house_data)
            if house_data['latitude'] is not None:
                sd.write(house_data, housekeeping_keys)
                #print(house_data)
                radio.run(house_data)
                time.sleep(1)
    finally:
        sd.teardown()  #teardown function to clean up the SD card
    
if __name__ == "__main__":
    main()
    
    
 
#with open(file, 'r) as f:

