import machine
import sdcard
import uos

housekeeping_keys = ["hhmmss","latitude","longitude","altitude","hdop","int_temp","ext_temp","Pressure"]
# Assign chip select (CS) pin (and start it high)
#cs = machine.Pin(9, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
class sd_card:
    def __init__(self,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=machine.Pin(6),mosi=machine.Pin(7),miso=machine.Pin(0),cs = machine.Pin(1, machine.Pin.OUT)):
        self.spi= machine.SPI(0,
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
            print("NO SD CARD SOZ....")
        
    def setup(self):
        try:
            vfs = uos.VfsFat(self.sd)
            uos.mount(vfs, "/sd")
            self.scan_devices()
            print("SD Card is setup...")
        except:
            print("SD Card IS NOT setup....")
        
    def write(self, telemetry, keys,name):
        try:
            with open(f"/data/{name}.txt", "a") as file:
                #print(telemetry)
                for key in keys:
                    file.write(str(telemetry[key]) + "," )
                file.write("\n")
            file.close
            print('We are writing to the SD')
        except:
            print("Can´t write to the SD if no SD card.....")
        
    def teardown(self):
        uos.umount("/sd")
        print("SD Card is unmounted...")
        
            
def main():
    #cs = machine.Pin(1, machine.Pin.OUT)
    while True:
        telemetry = {"hhmmss":6767676,"latitude":34343,"longitude":34334,"altitude":3434,"hdop":3434,"int_temp":3434,"ext_temp":3434,"Pressure":34343}
        cs = machine.Pin(1, machine.Pin.OUT)
        print(cs)
        sd = sd_card()
        sd.setup()
        #data = sd.write(telemetry, housekeeping_keys)
        
if __name__ == "__main__":
    main()
     
