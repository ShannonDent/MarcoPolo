import time
from machine import UART, Pin

# Initialize UART0 for the sensor (TX=GP0, RX=GP1)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart.init(9600, bits=8, parity=None, stop=1)
time.sleep_ms(1500)

def listen_for_sentence(port, sentence_type):
    """Listen for NMEA sentence_type on GPS serial port."""
    try:
        sentence = port.readline()
        if sentence is None:
            print("No data received from UART.")
            return None
        
        try:
            sentence = sentence.decode("ASCII")
        except UnicodeDecodeError:
            print("Error: Unicode decoding failed. Ignoring malformed sentence.")
            return None

        if len(sentence) < 6:
            print("Error: Received an incomplete sentence.")
            return None
        
        sentence_id = sentence[3:6]
        if sentence_id == sentence_type:
            print("ID Matches:", sentence_id)
            return sentence
        else:
            print(f"Ignoring sentence with ID: {sentence_id}")
            return None
    
    except Exception as e:
        print(f"Error reading UART: {e}")
        return None

def parse_sentence(sentence):
    """Parses a sentence and returns a dictionary of relevant data."""
    try:
        key = sentence.split(',')
        raw_time = key[1] if len(key) > 1 else "N/A"
        hour = raw_time[:2] if len(raw_time) >= 2 else "--"
        minutes = raw_time[2:4] if len(raw_time) >= 4 else "--"
        seconds = raw_time[4:6] if len(raw_time) >= 6 else "--"

        print(f"The time is: {hour}:{minutes}:{seconds}\n")
        return {
            "Raw Time": raw_time,
            "Hour": hour,
            "Minutes": minutes,
            "Seconds": seconds,
            "Latitude": key[2] + " " + key[3] if len(key) > 4 else "N/A",
            "Longitude": key[4] + " " + key[5] if len(key) > 6 else "N/A",
            "Altitude": key[9] + " " + key[10] if len(key) > 10 else "N/A",
            "Sentence": sentence,
        }
    except Exception as e:
        print(f"Error parsing sentence: {e}")
        return None

def main():
    """Listen for a single GGA sentence."""
    sentence = listen_for_sentence(uart, 'GGA')
    if sentence:
        parsed_data = parse_sentence(sentence)
        if parsed_data:
            print("Parsed Data:", parsed_data)
        else:
            print("Failed to parse sentence.")
    else:
        print("No valid sentence received.")

# Run the main function in a loop
while True:
    main()
    time.sleep(1)
