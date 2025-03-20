# telecommand_receiver
from machine import UART, Pin
from tuppersat.radio import TupperSatRadio
import time

# UART and radio setup
UART_ID = 1
RX_PIN = 5 # radio antenna
TX_PIN = 0 # pico communication
BAUDRATE = 38400
ADDRESS = 0x6D
CALLSIGN = "SAT1"  # Change as needed

# Initialize UART
uart = UART(UART_ID, baudrate=BAUDRATE, rx=Pin(RX_PIN))

uart_picos = UART(0, baudrate=BAUDRATE, tx=Pin(TX_PIN))

# Initialize TupperSatRadio
radio = TupperSatRadio(uart, ADDRESS, CALLSIGN)

def listen_for_telecommand():
    print("Listening for Telecommand...")
    """Read data from UART and check if it contains 'TELE'."""
    sentence = uart.readline()  # Read a full line from UART
    if sentence:
        print(f"Raw Data Received: {sentence}")  # Debugging output
        if b"TELE" in sentence:  # Check if "TELE" is in the received bytes
            print("Valid command received! Sending OK...")
            tele_received = b"OK\n"
            uart_picos.write(tele_received)
            # Store sentence into SD card
            #radio.send_data("OK".encode('utf-8'))  # Encode the string to bytes before sending
    time.sleep(1)

# Main loop
def main():
    while True:
        listen_for_telecommand()
        #time.sleep(1)

