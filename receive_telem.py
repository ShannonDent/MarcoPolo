from machine import UART, Pin
from tuppersat.rhserial import RXHandler

UART_ID = 0
TX_PIN = 16
RX_PIN = 17

T3_BAUDRATE = 38400

def display(message):
    return print(repr(message))

def read_bytes(uart, handler):
    _byte = uart.read(1)
    if _byte:
        handler.update(_byte)

def main():
    # initialisation
    uart = UART(UART_ID, baudrate=T3_BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    handler = RXHandler(on_received=display)

    # main loop
    while True:
        read_bytes(uart, handler)


if name=="main":
    main()