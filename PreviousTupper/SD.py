import machine
from lib.SD_CARD import sdcard
import uos


# Intialize SPI peripheral (start with 1 MHz)
class sd_card:
    def __init__(self, baudrate=1000000, polarity=0, phase=0, bits=8, 
                 firstbit=machine.SPI.MSB, sck=machine.Pin(6), mosi=machine.Pin(7), 
                 miso=machine.Pin(0), cs=machine.Pin(1, machine.Pin.OUT)):
        self.spi = machine.SPI(0,
                               baudrate=baudrate,
                               polarity=polarity,
                               phase=phase,
                               bits=bits,
                               firstbit=firstbit,
                               sck=sck,
                               mosi=mosi,
                               miso=miso)
        try:
            self.sd = sdcard.SDCard(self.spi, cs)
        except:
            print("SD CARD NOT WORKING SOZ....")

    def setup(self):
        try:
            vfs = uos.VfsFat(self.sd)
            uos.mount(vfs, "/sd")
            print("SD Card is setup...")
        except:
            print("SD CARD NOT CONNECTED......")

    def write_housekeeping(self, telemetry, keys):
        try:
            with open("/data/housekeeping.txt", "a") as file:
                for key in keys:
                    file.write(str(telemetry[key]) + ",")
                file.write("\n")
            file.close
            print("Housekeeping data saved on SD...")
        except:
            print("NO DATA SAVED SON...")
        

    def write_payload(self, telemetry, keys):
        try:
            with open("/data/payload.txt", "a") as file:
                for key in keys:
                    file.write(str(telemetry[key]) + ",")
                file.write("\n")
            file.close
            print("Payload data saved on SD...")
        except:
            print("You can´t expect the SD card to write data when there is no SD card....")
        
        """
        with open("/data/housekeeping.txt", "r") as file:
            data = file.read()
            print(data)
            file.close()"""
        
    def write(self, path, telemetry):
        with open(path, "a") as file:
            file.write(telemetry)
            file.write("\n")
        print('Test writing...')

    def teardown(self):
        try:
            uos.umount("/sd")
            print("SD Card is unmounted...")
        except:
            print("No SD card to unmount...")


def main():
    housekeeping_keys = ["hhmmss", "latitude", "longitude",
                         "altitude", "hdop", "int_temp", "ext_temp", "Pressure"]
    telemetry = {"hhmmss": 6767676, "latitude": 34343, "longitude": 34334,
                 "altitude": 3434, "hdop": 3434, "int_temp": 3434, 
                 "ext_temp": 3434, "Pressure": 34343}
    sd = sd_card()
    sd.setup()
    data = sd.writehousekeeping(telemetry, housekeeping_keys)
    print(data)


if __name__ == "__main__":
    main()
