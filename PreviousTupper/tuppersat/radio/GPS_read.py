from machine import UART, Pin
import time

class GPS:
    def __init__(self, uart_number=0, baudrate=9600, tx_pin=16, rx_pin=17):
        self.uart = UART(uart_number, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.uart.init(bits=8, parity=None, stop=1, timeout=1000)
        self._data = {'latitude': [], 'longitude': [], 'altitude': [], 'time': []}

    def read_data(self):
        while True:
            try:
                line_bytes = self.uart.readline()
                line = line_bytes.decode("ascii")
                #print(line)#ask about having to change the uppercase/lowercase
                #print(line)
                data=self.parse_data(line)
                #time.sleep(1)  #Pause for 5 seconds
                #return data
            except UnicodeError as e:
                print(f"UnicodeError {e}")
        #return data
            


    def parse_data(self, line):
        '''if line[3:6]=="GGA":
            print(line)'''
        data_split = line.split(',')
            #print(data_split)
        if data_split[0] == "$GPGGA":
            #print(line)
            if data_split[3] == "N":
                self._data['time'].append(data_split[1])
                latitude_decimal = float(data_split[2]) * 1e-2
                lat_deg, lat_min = self.convert_to_deg(latitude_decimal, "N")
                self._data['latitude'].append((lat_deg, lat_min))
                
            elif data_split[3] == "S":
                self._data['time'].append(data_split[1])
                latitude_decimal = -float(data_split[2]) * 1e-2
                lat_deg, lat_min = self.convert_to_deg(latitude_decimal, "S")
                self._data['latitude'].append((lat_deg, lat_min))

            if data_split[5] == "E":
                longitude_decimal = float(data_split[4]) * 1e-2
                lon_deg, lon_min = self.convert_to_deg(longitude_decimal, "E")
                self._data['longitude'].append((lon_deg, lon_min))
            elif data_split[5] == "W":
                longitude_decimal = -float(data_split[4]) * 1e-2
                lon_deg, lon_min = self.convert_to_deg(longitude_decimal, "W")
                self._data['longitude'].append((lon_deg, lon_min))

            if data_split[10] == "M":
                print(data_split[9])
                self._data['altitude'].append(float(data_split[9]))
        print( self._data)
    
    
    def convert_to_deg(self, decimal, direction):
        degree = int(decimal)
        minute = (decimal - degree) * 60

        if direction == "N" or direction == "E":
            return degree, minute
        else:
            return -degree, minute


def main():
    while True:
        gps = GPS()
        odata = gps.read_data()
        #print(odata)
    
if __name__ == "__main__":
    main()