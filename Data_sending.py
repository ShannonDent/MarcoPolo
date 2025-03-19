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
    #print(f"I2C Devices Found: {devices}")

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

    global ds18b20_temp = read_ds18b20()
    global bme_pressure, bme_humidity = read_bme280()
    global ms5837_temp, ms5837_pressure = read_ms5837()

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

def main():
    """ Main function to continuously update and print sensor data. """
    setup_i2c()
    setup_temperature_sensors()
    read_calibration_constants()

    while True:
        time.sleep(5)         # Adjust delay as needed
        update_sensor_data()  # Update global variable
        #print(sensor_data)    # Print all sensor data in one line
        sensor_send = bytes(sensor_data, 'utf-8')
        radio.send_data(sensor_send)
        time.sleep(5)         # Adjust delay as needed
        send_telemetry(self, hhmmss, latitude, longitude, 1.2, altitude, ms5837_temp, ds18b20_temp, ms5837_pressure)

# Run the main function
if __name__ == "__main__":
    main()
