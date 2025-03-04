from tuppersat.radio.gps2 import GPS
from tuppersat.radio.Temperature import Temperature
from tuppersat.radio.Pressure import Pressure
ds_pin_ext = 18
ds_pin_int = 19
sensors = [GPS(), Temperature(ds_pin_ext), Temperature(ds_pin_int), Pressure()]

for sensor in sensors:
    sensor.setup()
    
while True:
    for sensor in sensors:
        sensor.read_data()
        print(sensor.data)
        
        
#with open(file, 'r) as f: