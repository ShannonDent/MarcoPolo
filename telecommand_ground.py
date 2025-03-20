# uPython imports
from machine import UART, Pin
import time

# tuppersat imports
from tuppersat.radio import TupperSatRadio

# Constants
address = 0x6D
callsign = 'TELE1'
BAUDRATE = 38400

# Create UART interface
uart = UART(0, baudrate=BAUDRATE, tx=Pin(16), rx=Pin(17))

# Create radio object
radio = TupperSatRadio(uart, address, callsign)

while True:
    # Encode and send a properly formatted string message
    message = "TELE1:DATA=2"  # Properly formatted command
    radio.send_data(message.encode("utf-8"))  # Convert string to bytes
    
    print(f"Sent: {message}")  # Debugging output
    time.sleep(1)
