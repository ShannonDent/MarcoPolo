import machine
import time
import onewire
import ds18x20

class Temperature:
    def __init__(self, pin):
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(pin)))
        self.roms = self.ds_sensor.scan()
        self.data = []
        self.pin = pin
        
    def setup(self):
        if self.pin == 22:
            print("External Temperature sensor is setup...")
        elif self.pin == 14:
            print("Internal Tepmerature Sensor is setup...")
        

    def read_data(self):
        #print(self.roms)
        try:
            self.ds_sensor.convert_temp()
            for rom in self.roms:
                self.data = self.ds_sensor.read_temp(rom)
        except:
            print("An error occurred for temperature sensor...")
            self.data = 0.0
    

    """def run(self):
        #print('Found DS devices:', self.roms)
        try:
            self.data = self.read_data()
            return tempC
        except Exception as e:
            print("An error occurred:", e)"""
            
        

def main():
    #temp = Temperature()
    ds_pin_ext = machine.Pin(22)
    ds_pin_int = machine.Pin(14)
    external_temp = Temperature(ds_pin_ext)
    internal_temp = Temperature(ds_pin_int)
    while True:
        temp1 = external_temp.read_data()
        temp2 = internal_temp.read_data()
        #print(temp1,temp2)
        print("ext = ", external_temp.data)
        print("int = ", internal_temp.data)
        
    #return temp1, temp2

if __name__ == "__main__":
    main() 