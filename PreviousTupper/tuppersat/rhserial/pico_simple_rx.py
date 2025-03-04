"""pico_simple_rx.py

A test script demonstrating a simple message receiver with the RHSerial library
and a synchronous UART serial port. This is compatible with MicroPython on the
Raspberry Pi Pico.

"""

# micropython imports
from machine import UART, Pin

# tuppersat imports
from tuppersat.rhserial import RXHandler


# constants
UART_ID = 1
TX_PIN = 4
RX_PIN = 5

T3_BAUDRATE = 38400

def display(message):
    return print(repr(message))

def loop(uart, handler):
    _byte = uart.read(1)
    if _byte:
        handler.update(_byte)

def main():
    # initialisation
    uart = UART(UART_ID, baudrate=T3_BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    handler = RXHandler(on_received=display)    

    # main loop
    while True:
        loop(uart, handler)

        
if __name__=="__main__":
    main()
