# Import necessary libraries
from machine import Pin, I2C
from time import sleep
import onewire, ds18x20
import bme280
from machine import UART
from ucollections import namedtuple
import time
from tuppersat.radio import TupperSatRadio

# Constants for I2C addresses and sensor pins
MS5837_ADDR = 0x77
BME280_I2C_ADDR = 0x76  # Adjust if necessary
ADDRESS = 0x6D
CALLSIGN = 'TELE1'
BAUDRATE = 38400

# Create UART interface for radio communication
uart = UART(0, baudrate=BAUDRATE, tx=Pin(12), rx=Pin(13))
radio = TupperSatRadio(uart, ADDRESS, CALLSIGN)

# Initialize I2C interfaces
i2c_bme = I2C(1, scl=Pin(3), sda=Pin(2))  # BME280 I2C
i2c_other = I2C(0, scl=Pin(1), sda=Pin(0))  # MS5837 I2C

# Initialize OneWire for DS18B20 sensors
one_wire_pin = Pin(15)
temperature_sensors = ds18x20.DS18X20(onewire.OneWire(one_wire_pin))

# Function to unpack MS5837 data from bytes
def unpack(buffer):
    """ Unpacks MSB-ordered buffer of bytes into an unsigned integer. """
    return sum(byte << (i * 8) for i, byte in enumerate(reversed(buffer)))

# Function to read MS5837 calibration constants
def read_calibration_constants():
    global calibration_constants
    registry_positions = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]
    
    try:
        cbytes = [i2c_other.readfrom_mem(MS5837_ADDR, reg, 2) for reg in registry_positions]
        calibration_constants = [unpack(cb) for cb in cbytes]
        print(f"Calibration Constants (MS5837): {calibration_constants}")
    except Exception as e:
        print(f"Error reading calibration constants: {e}")
        calibration_constants = []

# Function to read ADC from MS5837
def read_adc(command):
    try:
        i2c_other.writeto(MS5837_ADDR, command)
        sleep(0.5)
        return unpack(i2c_other.readfrom_mem(MS5837_ADDR, 0x00, 3))
    except Exception as e:
        print(f"Error reading ADC data: {e}")
        return None

# Function to read data from MS5837
def read_ms5837():
    if not calibration_constants:
        print("Error: Calibration constants not loaded!")
        return None, None
    
    TEMPERATURE_ADC = b'\x48'
    PRESSURE_ADC = b'\x58'
    
    D2 = read_adc(TEMPERATURE_ADC)
    D1 = read_adc(PRESSURE_ADC)
    
    if D2 is None or D1 is None:
        print("Error: Failed to read ADC values.")
        return None, None
    
    dt = D2 - calibration_constants[4] * (2 ** 8)
    TEMP = 2000 + dt * calibration_constants[5] / (2 ** 23)
    
    OFF = calibration_constants[1] * (2 ** 16) + (calibration_constants[3] * dt) / (2 ** 7)
    SENS = calibration_constants[0] * (2 ** 15) + (calibration_constants[2] * dt) / (2 ** 8)
    P = (D1 * SENS / (2 ** 21) - OFF) / (2 ** 15)
    
    return TEMP / 100, P / 100

# Function to read BME280 data
def BME_Data():
    try:
        bme = bme280.BME280(i2c=i2c_bme)  # BME280 object created
        return bme.values[1], bme.values[2], bme.values[0]  # Pressure, Humidity, Temperature
    except Exception as e:
        print(f"BME280 Error: {e}")
        return None, None, None

# Function to read DS18B20 data
def Temp_Data():
    temperature_sensors.convert_temp()
    temps = {}
    for rom in temperature_sensors.scan():
        tempC = temperature_sensors.read_temp(rom)
        # Convert ROM to hashable string
        rom_str = ''.join(['{:02x}'.format(byte) for byte in rom])
        temps[rom_str] = tempC
    return temps

# Function to create telemetry packet
def create_telemetry_packet():
    pressure_bme, humidity_bme, temperature_bme = BME_Data()
    temp_data_ds18b20 = Temp_Data()
    temperature_ms5837, pressure_ms5837 = read_ms5837()

    # Check if we got valid MS5837 data
    if temperature_ms5837 is None or pressure_ms5837 is None:
        print("Error reading MS5837 data!")
        return None

    # Format the telemetry data into a string
    telemetry_string = f"BME280 Pressure: {pressure_bme} mbar, Humidity: {humidity_bme} %, Temperature: {temperature_bme} °C; "
    telemetry_string += f"DS18B20 Temps: {temp_data_ds18b20}; "
    telemetry_string += f"MS5837 Temp: {temperature_ms5837} °C, Pressure: {pressure_ms5837} mbar"

    # Encode the telemetry data as bytes for transmission
    return telemetry_string.encode('utf-8')

# Read calibration constants before starting the loop
read_calibration_constants()

# Main loop to send telemetry data
while True:
    telemetry_packet = create_telemetry_packet()

    # Only send data if it is valid
    if telemetry_packet:
        telecommand_dict = {
            'data': telemetry_packet
        }
        
        # Send telemetry data via radio
        radio.send_data(**telecommand_dict)
        print(f"Sending Telemetry: {telemetry_packet.decode('utf-8')}")
    
    time.sleep_ms(1000)  # Adjust sleep time as necessary
