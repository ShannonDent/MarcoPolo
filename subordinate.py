from machine import Pin, SPI
import time

# Initialize SPI (Donkey Mode)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
cs = Pin(5, Pin.IN)  # Chip Select (CS)

def receive_message():
    while cs.value() == 1:  # Wait for CS to go low
        pass
    msg = spi.read(13)  # Read data (10 bytes max)
    txdata = b'Hello Shrekk'
    rxdata = bytearray(len(txdata))
    spi.write_readinto(txdata, rxdata)  # Send response
    #time.sleep(0.1)  # Give time for response
    #return msg.decode('utf-8').strip()
    return msg

while True:
    received = receive_message()
    print("Donkey: Received ->", received)


