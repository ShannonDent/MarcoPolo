"""pico_simple_tx.py

A test script demonstrating simple transmission with the RHSerial library and a
synchronous UART serial port. This is compatible with MicroPython on the
Raspberry Pi Pico.

"""

# standard library imports
import time

# micropython imports
from machine import UART, Pin

# tuppersat imports
from tuppersat.rhserial import pack_message

# constants
UART_ID = 1
TX_PIN = 4
RX_PIN = 5

T3_BAUDRATE = 38400

def counter(start=0x00, modulo=None):
    """Callable that counts from start every time it is called."""
    _count = start

    def _counter():
        nonlocal _count
        idx = _count
        # update counter
        _count += 1
        if modulo:
            _count %= modulo
        return idx

    return _counter


def send(uart, data):
    print('Sending: ',end='')
    print(repr(data))
    uart.write(data)

def loop(uart, message, msg_to, msg_from, msg_count, pause=1):
    _data = pack_message(message, msg_to, msg_from, msg_count())
    send(uart, bytes(_data))
    time.sleep(pause)
    
def main():
    # initialisation
    uart = UART(UART_ID, baudrate=T3_BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN))

    _msgbytes = b'hello, world!'
    _msgto = 0xff
    _msgfrom = 0x00
    _msgid = counter(modulo=0xff)

    # main loop
    while True:
        loop(uart, _msgbytes, _msgto, _msgfrom, _msgid)

if __name__=="__main__":
    main()
