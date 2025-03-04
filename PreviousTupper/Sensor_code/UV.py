import machine
import time
import Sensor_code.iorodeo_as7331 as as7331
from SD import sd_card
import time

class UV:
    def __init__(self):
        sclpin = machine.Pin(19)
        sdapin = machine.Pin(18)
        self.i2c_bus = machine.I2C(1, scl=sclpin, sda=sdapin)
        self.sensor = as7331.AS7331(self.i2c_bus)
        self.sensor.gain = as7331.GAIN_512X
        self.sensor.integration_time = as7331.INTEGRATION_TIME_128MS
        self.data = []

    def scan_devices(self):
        self.i2c_bus.scan()

    def setup(self):
        try:
            #self.scan_devices()
            print("UV Sensor is setup...")
        except:
            print("UV sensor not connected...")

    def read_data(self):
        try:
            uva, uvb, uvc, temp = self.sensor.values
            self.data = [uva, uvb, uvc, temp]
        except:
            print("UV sensor is disconnected")


def main():
    uv = UV()
    uv.setup()
    sd = sd_card()
    sd.setup()
    n=0
    while True:
        uv.read_data()
        #uva, uvb, uvc, temp = UV().read_data()
        c = f'N: {n}, uva: {uv.data[0]:1.2f}, uvb: {uv.data[1]:1.2f}, uvc: {uv.data[2]:1.2f}, temp: {uv.data[3]:1.2f}'
        print(c)
        time.sleep(1)
        sd.write("/data/uvtest3.txt", c)
        n +=2
        


if __name__ == "__main__":
    main()
