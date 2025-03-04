# This is potential, untested updated GPS code, will need to test it on Monday. It is not saved to the Pico but
# it is saved onto my computer - Ross :) 


from machine import UART, Pin
import time

class GPSSensor:
    def _init_(self):
        self.G = 0  
        self.uart = None
        self.baudrate = 9600
        self.txpin = 0
        self.rxpin = 1
        
    def setup(self):
        self.uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17), timeout=100, rxbuf=128)
        
    def read(self, max_attempts=6):
        print(self.uart.readline().decode("ASCII"))
        attempts = 0
        while attempts < max_attempts:
            if self.uart.any():
                try:
                    data = self.uart.readline()
                    
                    if data:
                        decoded_data = data.decode("ASCII").strip()
                        if decoded_data.startswith("$GPGGA"):
                            parts = decoded_data.split(",")
                            if len(parts) >= 15 and parts[2] and parts[4]:
                                return {
                                    "Latitude": parts[2],
                                    "Longitude": parts[4],
                                    "Hdop": parts[8],
                                    "Altitude": parts[9],
                                    "Time": parts[1][0:2] + "," + parts[1][2:4] + "," + parts[1][4:6]
                                }
                except UnicodeError as e:
                    print("UnicodeError occurred:", e)
            time.sleep(1)  # Wait a bit before trying again
            attempts += 1
        
        # Return a default value if no valid data is received after max_attempts
        return {
            "Latitude": '0',
            "Longitude": '0',
            "Hdop": '0',
            "Altitude": '0',
            "Time": '000000'
        }

def main():
    gps = GPSSensor()
    gps.setup()
    gps_data = gps.read()  # This will now try up to 6 times to get valid data
    print("GPS Data:", gps_data)
    if gps_data['Hdop'] != '0':
        print("GPS Data Valid:", gps_data)
            
if __name__ == "__main__":
    main()