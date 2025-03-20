from machine import UART, Pin
import time
from tuppersat.rhserial import RXHandler
import telecommand_receiver

def display(message):
    return print(repr(message))

def read_bytes(uart, handler):
    _byte = uart.read(1)
    if _byte:
        handler.update(_byte)

# UART 1 for radio reception
uart_antenna = UART(1, baudrate=38400, rx=Pin(5))
handler = RXHandler(on_received=display)

# UART 1 for communication with Master Pico
uart1 = UART(0, baudrate=38400, tx=Pin(0))

# LED indicator
led = Pin(25, Pin.OUT)

while True:
    led_off = b"0\n"
    led_on = b"1\n"
    # **Step 1: Send LED toggle commands to Master**
    uart1.write(led_on)
    print("Sent LED ON Command:", led_on)  # Debugging
    time.sleep(2)  # Avoid flooding messages
    print("Sent:", led_on)

    uart1.write(led_off)
    print("Sent LED OFF Command:", led_off)  # Debugging
    time.sleep(2)
    print("Sent:", led_off)

    # **Step 2: Read radio antenna**
    if uart_antenna.any():  # Check if data is available
        try:
            data = uart_antenna.readline()
            if data is None:
                continue  # Skip processing if no data received
            
            #if isinstance(data, bytes):  # Decode only if data is in bytes
            #    data = data.decode('utf-8').strip()
            #else:
            #    data = data.strip()  # If it's already a string, just strip it
            
            if data:
                print("Received:", data)
                #log_data(data)
                
                # Blink LED to indicate reception
                led.value(1)
                time.sleep(0.1)
                led.value(0)
        except Exception as e:
            print("Error receiving data:", e)
    
    time.sleep(0.1)
    
    # **Step 3: Listen for Telecommands
    telecommand_receiver.listen_for_telecommand()
