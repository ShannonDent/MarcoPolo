from machine import Pin, SPI
import time

# Initialize SPI (Shrek Mode)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
cs = Pin(5, Pin.OUT)  # Chip Select

def send_message(message):
    cs.value(0)  # Enable Donkey
    time.sleep(0.1)
    txdata = b'Hello Donkey'
    rxdata = bytearray(len(txdata))
    spi.write_readinto(txdata, rxdata)  # Send Data
    time.sleep(0.1)  # Give time for response
    response = spi.read(13)  # Read response (10 bytes max)
    time.sleep(0.1)  # Give time for response
    cs.value(1)  # Disable Donkey
    #return response.decode('utf-8').strip()
    return response

while True:
    msg = "Hello Donkey"
    print("Shrek: Sending ->", msg)
    
    response = send_message(msg)
    if response == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
        response = None
    print("Shrek: Received ->", response)
    
    time.sleep(2)  # Wait before next transmission


