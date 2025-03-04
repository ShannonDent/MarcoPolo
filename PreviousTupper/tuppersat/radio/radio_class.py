from time import sleep
from machine import UART, Pin
from tuppersat.radio import TupperSatRadio
#from tuppersat.radio.GPS_read import GPS
from ucollections import namedtuple
from tuppersat.radio._packet_utils import TelemetryPacket, DataPacket

# constants
UART_ID = 1
TX_PIN = 4
RX_PIN = 5
T3_BAUDRATE = 38400

ADDRESS = 0xfa
CALLSIGN = 'MOUSE'

Time = namedtuple('Time', 'hour minute second microsecond')

class Radio:
    def __init__(self, uart_id=1, tx_pin=4, rx_pin=5, address=0xfe, callsign='MOUSE', baudrate=38400):
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.address = address
        self.callsign = callsign
        self.baudrate = baudrate
        self.uart = None
        self.radio = None

        self.setup()
    

    def setup(self):
        try:
            self.uart = UART(self.uart_id, baudrate=self.baudrate, tx=Pin(self.tx_pin), rx=Pin(self.rx_pin))
            self.radio = TupperSatRadio(self.uart, self.address, self.callsign)
            print("Radio is setup....")
        except:
            print("Radio is NOT setup....")

    def send_telemetry(self, telemetry_data):
        self.radio.send_telemetry(**telemetry_data)
                
    def send_data(self, telemetry_data):
        self.radio.send_data(**telemetry_data)
        
    def chunk(self,string, n):
        """Break a string into chunks of length n."""
        return (string[i:i+n] for i in range(0, len(string), n))

    def parse_time(self,time_str):
        """Parse a time string HHMMSS.SSS into a Time object."""
        
        # split out the second and sub-second times
        _hhmmss, _milliseconds = time_str.split('.')

        # compute the sub-second time in microseconds
        _us = int(_milliseconds) * 1000

        # compute the hours, minutes and seconds
        _hh, _mm, _ss = (int(x) for x in self.chunk(_hhmmss, 2))

        return Time(_hh, _mm, _ss, _us)

    def run(self, telemetry_data):
        try:
            if len(telemetry_data) == 8:
                    #print(len(telemetry_data))
                    #print(telemetry_data['hdop'],telemetry_data['longitude'])
                    print('Sending Housekeeping telemetry')
                    self.send_telemetry({
                        'hhmmss': self.parse_time(telemetry_data['hhmmss']),
                        'latitude': telemetry_data['latitude'],
                        'longitude': telemetry_data['longitude'],
                        'hdop': telemetry_data['hdop'],
                        'altitude': telemetry_data['altitude'],
                        't_internal': telemetry_data['int_temp'],
                        't_external': telemetry_data['ext_temp'],
                        'pressure': telemetry_data['Pressure']})
            elif len(telemetry_data) == 6:
                    #print(len(telemetry_data))
                    print('Sending Payload telemetry')
                    self.send_data({
                        'hhmmss': self.parse_time(telemetry_data['hhmmss']),
                        'UVA': telemetry_data['UVA'],
                        'UVB': telemetry_data['UVB'],
                        'UVC': telemetry_data['UVC'],
                        'Ozone': telemetry_data['Ozone'],
                        'Temp': telemetry_data['Temp'],
                        })
        except:
            print("Radio is not able to send telemetry...")
                    
                    
            

def main():
    while True:
        telemetry_data = {
            'hhmmss': str(324243.223),
            'latitude': None,
            'longitude': None,
            'hdop':None,
            'int_temp': None,
            'ext_temp': None,
            'Pressure': None,
            'altitude': None
        }
        print(len(telemetry_data))
        radio = Radio()
        radio.setup()
        radio.run(telemetry_data)

if __name__ == "__main__":
    main()