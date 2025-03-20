from machine import UART, Pin
from ucollections import namedtuple
import time

# TupperSat imports
from tuppersat.radio import TupperSatRadio

# UART 1 setup (Same UART for both LED commands and telemetry)
uart1 = UART(1, baudrate=38400, tx=Pin(4), rx=Pin(5))

# Onboard LED setup
led = Pin("LED", Pin.OUT)

# Radio Configuration
address = 0x6D
callsign = 'MarcoPolo'
radio = TupperSatRadio(uart1, address, callsign)

# Define telemetry data structure
Time = namedtuple('Time', 'hour minute second microsecond')
telemetry_dict = {
    'hhmmss': Time(hour=12, minute=34, second=56, microsecond=0),
    'latitude': 53.3096,
    'longitude': -6.2186,
    'hdop': 1.53,
    'altitude': 121.4,
    't_internal': 21.062,
    't_external': -7.562,
    'pressure': 980.0274,
}

# Main loop
count = 0
while True:
    # **Step 1: Read LED command from Slave (if available)**
    if uart1.any():  # Check if data is available
        message = uart1.readline()
        if message:
            message = message.strip()  # Remove whitespace/newline
            print("Received LED Command:", message)
            if message == b"1":
                print("Turning LED ON")  # Debugging
                led.value(1)  # Turn LED ON
            elif message == b"0":
                print("Turning LED OFF")  # Debugging
                led.value(0)  # Turn LED OFF

    # **Step 2: Send telemetry every 2 seconds**
    if count % 2 == 0:
        radio.send_telemetry(**telemetry_dict)
        print("Sending Telemetry", telemetry_dict)

    count += 1
    time.sleep(2)
