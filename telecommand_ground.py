# uPython imports
from machine import UART, Pin
from ucollections import namedtuple
#from datetime import datetime as dt
import time

# tuppersat imports
from tuppersat.radio import TupperSatRadio

# constants
address = 0x6D
callsign = 'TELE1'
BAUDRATE = 38400

# create the UART interface
uart = UART(0, baudrate=BAUDRATE, tx=Pin(0), rx=Pin(1))

radio = TupperSatRadio(uart, address, callsign)

Time = namedtuple('Time', 'hour minute second microsecond')

def chunk(string, n):
    """Break a string into chunks of length n."""
    return (string[i:i+n] for i in range(0, len(string), n))

def parse_time(time_str):
    """Parse a time string HHMMSS.SSS into a Time object."""

    # split out the second and sub-second times
    _hhmmss, _milliseconds = time_str.split('.')

    # compute the sub-second time in microseconds
    _us = int(_milliseconds) * 1000

    # compute the hours, minutes and seconds
    _hh, _mm, _ss = (int(x) for x in chunk(_hhmmss, 2))

    return Time(_hh, _mm, _ss, _us)

telemetry_dict = {
    'data' : 1,
}

while True:
    radio.send_data(**telemetry_dict)
    time.sleep_ms(1000)
    print("Sending Telemetry")


