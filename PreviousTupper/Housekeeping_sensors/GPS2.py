from machine import UART, Pin
import time
from Housekeeping_sensors.gps_airborne import set_airborne_mode

class GPS:
    def __init__(self, uart_number=1, baudrate=9600, tx_pin=8, rx_pin=9):
        self.uart_number = uart_number
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.uart = None
        self.data = ('11', '11', '11', '111111.000', '11')
        self.id = "GGA"

    def check_sentence(self, sentence):
        if sentence[3:6] == self.id:
            # print()
            return True

    def setup(self):
        self.uart = UART(self.uart_number, baudrate=self.baudrate, tx=Pin(
            self.tx_pin), rx=Pin(self.rx_pin), rxbuf=1024, timeout=40, timeout_char=10)
        self.uart.init(bits=8, parity=None, stop=1, timeout=10000)
        print("GPS is setup...")
        set_airborne_mode(self.uart)
        time.sleep(1)
        print("GPS set to airborne...")

    def read_data(self):
        # print('reading...')
        try:
            for i in range(10):
                line_bytes = self.uart.readline().decode("ascii")
                data_split = line_bytes.split('$')
                # print(data_split)
                for string in data_split:
                    # print(string)
                    if string[:5] == 'GPGGA':
                        # print(string)
                        self.data = parse_data(string)
                        # print(self.data)
        except UnicodeError:
            print("Unicode error occurred. Continuing...")
            return ""


def parse_data(line):
    if line is None:
        return '22', '22', '22', '222222.222', '22'
    elif line is not None:
        # print(line)
        data_split = line.split(',')
        if len(data_split) >= 10:
            for i in range(len(data_split)):
                if data_split[i] == '':
                    data_split[i] = '000000.000'
            time_val = data_split[1]
            lat = data_split[2]
            lon = data_split[4]
            alt = data_split[9]
            hdop = data_split[8]
        #print(lat, lon, alt, time_val, hdop)
            return lat, lon, alt, time_val, hdop
        else:
            # print(data_split)
            return '99', '99', '99', '999999.000', '99'


def main():
    gps = GPS()
    gps.setup()
    while True:
        time.sleep(1)
        gps.read_data()
        print(gps.data)
        # print('test')


if __name__ == "__main__":
    main()