import machine
import time
import onewire, ds18x20
import bme280       
from tuppersat.radio import TupperSatRadio
from machine import UART, Pin

# I2C address for MS5837 sensor
MS5837_ADDR = 119  # 0x77

# Constants for I2C addresses and sensor pins
ADDRESS = 0x6D
CALLSIGN = 'MarcoPolo'
BAUDRATE = 38400

# Create UART interface for radio communication
uart = UART(1, baudrate=BAUDRATE, tx=Pin(8), rx=Pin(9))
radio = TupperSatRadio(uart, ADDRESS, CALLSIGN)

# Initialize UART0 for GPS (RX=GP13)
uart_gps = UART(0, baudrate=9600, rx=Pin(13))
uart_gps.init(9600, bits=8, parity=None, stop=1)
time.sleep_ms(1500)

# Global variables for GPS data (initialized as "N/A" but updated with last valid values)
hhmmss = "N/A"
latitude = "N/A"
longitude = "N/A"
altitude = "N/A"
hdop = "N/A"

# Global variables
i2c = None
temperature_sensors = None
roms = None
calibration_constants = []
sensor_data = "Initializing..."  # Global variable to store sensor readings


def setup_i2c():
    """ Initializes I2C communication and scans for devices. """
    global i2c
    i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
    
    devices = i2c.scan()
    print(f"I2C Devices Found: {devices}")

    if MS5837_ADDR not in devices:
        print("Warning: MS5837 sensor not detected!")

    return i2c

def setup_temperature_sensors():
    """ Initializes OneWire and scans for DS18B20 temperature sensors. """
    global temperature_sensors, roms
    one_wire_pin = machine.Pin(15)
    temperature_sensors = ds18x20.DS18X20(onewire.OneWire(one_wire_pin))
    
    # Scan for DS18B20 devices
    roms = temperature_sensors.scan()
    print(f"Found {len(roms)} DS18B20 temperature sensors: {roms}")

def read_bme280():
    """ Reads pressure & humidity from BME280 sensor. """
    try:
        bme = bme280.BME280(i2c=i2c)  # Initialize BME280
        return float(bme.values[1].replace("hPa", "").strip()), float(bme.values[2].replace("%", "").strip())
    except Exception as e:
        print(f"BME280 Error: {e}")
        return None, None

def read_ds18b20():
    """ Reads temperature from all DS18B20 sensors and returns the average value. """
    try:
        temperature_sensors.convert_temp()  # Start conversion
        time.sleep(0.75)  # Wait for conversion

        temperatures = [temperature_sensors.read_temp(rom) for rom in roms]
        return sum(temperatures) / len(temperatures) if temperatures else None
    except Exception as e:
        print(f"DS18B20 Error: {e}")
        return None

def unpack(buffer):
    """ Unpacks MSB-ordered buffer of bytes into an unsigned integer. """
    _buffer = reversed(bytearray(buffer))
    return sum(_byte << (_i * 8) for _i, _byte in enumerate(_buffer))

def read_calibration_constants():
    """ Reads and unpacks calibration constants from the MS5837 sensor. """
    global calibration_constants
    registry_positions = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]

    try:
        cbytes = [i2c.readfrom_mem(MS5837_ADDR, reg, 2) for reg in registry_positions]
        calibration_constants = [unpack(cb) for cb in cbytes]

        print(f"Calibration Constants (MS5837): {calibration_constants}")
    except Exception as e:
        print(f"Error reading calibration constants: {e}")
        calibration_constants = []

def read_adc(command):
    """ Sends a command to the sensor and reads a 3-byte ADC value. """
    try:
        i2c.writeto(MS5837_ADDR, command)
        time.sleep_ms(500)  # Wait for conversion
        return unpack(i2c.readfrom_mem(MS5837_ADDR, 0x00, 3))
    except Exception as e:
        print(f"Error reading ADC data: {e}")
        return None

def read_ms5837():
    """ Reads ADC values and calculates temperature & pressure from MS5837. """
    if not calibration_constants:
        print("Error: Calibration constants not loaded!")
        return None, None

    TEMPERATURE_ADC = b'\x48'
    PRESSURE_ADC = b'\x58'

    # Read ADC values
    D2 = read_adc(TEMPERATURE_ADC)  # Temperature ADC
    D1 = read_adc(PRESSURE_ADC)  # Pressure ADC

    if D2 is None or D1 is None:
        print("Error: Failed to read ADC values.")
        return None, None

    # Calculate temperature
    dt = D2 - calibration_constants[4] * (2 ** 8)
    TEMP = 2000 + dt * calibration_constants[5] / (2 ** 23)

    # Calculate pressure
    OFF = calibration_constants[1] * (2 ** 16) + (calibration_constants[3] * dt) / (2 ** 7)
    SENS = calibration_constants[0] * (2 ** 15) + (calibration_constants[2] * dt) / (2 ** 8)
    P = (D1 * SENS / (2 ** 21) - OFF) / (2 ** 15)

    return round(TEMP / 100, 2), round(P / 100, 2)

def update_sensor_data():
    """ Updates the global `sensor_data` string with current sensor values. """
    global sensor_data

    global ds18b20_temp, bme_pressure, bme_humidity, ms5837_temp, ms5837_pressure
    ds18b20_temp = read_ds18b20()
    bme_pressure, bme_humidity = read_bme280()
    ms5837_temp, ms5837_pressure = read_ms5837()


    # Ensure values are formatted and default to "N/A" if missing
    ds18b20_temp_str = f"{ds18b20_temp:.2f}" if ds18b20_temp is not None else "N/A"
    bme_pressure_str = f"{bme_pressure:.2f}" if bme_pressure is not None else "N/A"
    bme_humidity_str = f"{bme_humidity:.2f}" if bme_humidity is not None else "N/A"
    ms5837_temp_str = f"{ms5837_temp:.2f}" if ms5837_temp is not None else "N/A"
    ms5837_pressure_str = f"{ms5837_pressure:.2f}" if ms5837_pressure is not None else "N/A"

    # Store the sensor values as a single formatted string
    sensor_data = (
        f"DS18B20 Temp:{ds18b20_temp_str}|"
        f"BME280 Pressure:{bme_pressure_str}hPa|"
        f"BME280 Humidity:{bme_humidity_str}%|"
        f"MS5837 Temp:{ms5837_temp_str}|"
        f"MS5837 Pressure:{ms5837_pressure_str}hPa"
    )


def read_gps_sentence():
    """Reads and returns a clean $GPGGA sentence from the GPS module."""
    try:
        while True:
            sentence = uart_gps.readline()
            if sentence is None:
                return None  # No data received
            
            try:
                sentence = sentence.decode("ASCII").strip()
            except:
                return None  # Ignore malformed data

            if sentence.startswith("$GPGGA"):  
                return sentence  # Only return GGA sentences
            else:
                #print(f"Ignoring non-GGA sentence: {sentence[:6]}")
                return None  # Ignore malformed data

    except Exception as e:
        print(f"Error reading GPS: {e}")
        return None
    
def clearbuffer():
    """Clears Buffer GPS"""
    #while uart_gps.any():
    #    print("emptying buffer")
    uart_gps.read()
    time.sleep(1)
    print("empty buffer")

def parse_gga(sentence):
    """Parses a GGA sentence and updates global GPS variables, removing N/S/E/W from lat/lon."""
    global hhmmss, latitude, longitude, altitude, hdop  

    try:
        parts = sentence.split(',')
        
        if len(parts) < 10:  # Ensure enough fields exist
            print("Incomplete GGA sentence received.")
            return

        # Extract time safely (Always updates)
        hhmmss = parts[1] if parts[1] else hhmmss

        # Extract and update latitude if valid (remove N/S)
        lat_value = parts[2]
        if lat_value:
            latitude = f"{lat_value[:2]}.{lat_value[2:]}"  # Keep decimal format
          
        # Extract and update longitude if valid (remove E/W)
        lon_value = parts[4]
        if lon_value:
            longitude = f"{lon_value[:3]}.{lon_value[3:]}"  # Keep decimal format

        # Extract and update HDOP if valid
        if parts[8]:
            hdop = parts[8]

        # Extract and update altitude if valid
        if parts[9]:
            altitude = f"{parts[9]}"

        print(f"Time (hhmmss): {hhmmss}, Latitude: {latitude}, Longitude: {longitude}, HDOP: {hdop}, Altitude: {altitude}")

    except Exception as e:
        print(f"Error parsing GGA: {e}")

def main():
    """Continuously read sensor data and parse GPS data while keeping the last known valid values."""
    
    setup_i2c()
    setup_temperature_sensors()
    read_calibration_constants()

    while True:
        #Sensors
        update_sensor_data()  # Update global variable
        print(sensor_data)    # Print all sensor data in one line
          
        #GPS 
        sentence = read_gps_sentence()
        if sentence:
            parse_gga(sentence)
            #clearbuffer()
        #time.sleep(1)

        #Send Data + Telemetry
        #sensor_send = bytes(sensor_data, 'utf-8')
        #radio.send_data(sensor_send)
        #send_telemetry(self, hhmmss, latitude, longitude, hdop, altitude, ms5837_temp, ds18b20_temp, ms5837_pressure)


# Run the script
main()

