import machine
import time
import onewire, ds18x20
import bme280       

# I2C address for MS5837 sensor
MS5837_ADDR = 119  # 0x77

# Global variables
i2c = None
temperature_sensors = None
roms = None
calibration_constants = []


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
    """ Reads and prints pressure & humidity from BME280 sensor. """
    try:
        bme = bme280.BME280(i2c=i2c)  # Initialize BME280
        print(f"\nPressure (BME280): {bme.values[1]}")
        print(f"Humidity (BME280): {bme.values[2]}")
    except Exception as e:
        print(f"BME280 Error: {e}")


def read_ds18b20():
    """ Reads temperature from all DS18B20 sensors and prints the values. """
    temperature_sensors.convert_temp()  # Start temperature conversion
    time.sleep(0.75)  # Wait for conversion

    for i, rom in enumerate(roms, start=1):
        tempC = temperature_sensors.read_temp(rom)
        print(f"Temp Sensor {i}: {tempC:.2f}°C")


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
        return

    TEMPERATURE_ADC = b'\x48'
    PRESSURE_ADC = b'\x58'

    # Read ADC values
    D2 = read_adc(TEMPERATURE_ADC)  # Temperature ADC
    D1 = read_adc(PRESSURE_ADC)  # Pressure ADC

    if D2 is None or D1 is None:
        print("Error: Failed to read ADC values.")
        return

    # Calculate temperature
    dt = D2 - calibration_constants[4] * (2 ** 8)
    TEMP = 2000 + dt * calibration_constants[5] / (2 ** 23)

    # Calculate pressure
    OFF = calibration_constants[1] * (2 ** 16) + (calibration_constants[3] * dt) / (2 ** 7)
    SENS = calibration_constants[0] * (2 ** 15) + (calibration_constants[2] * dt) / (2 ** 8)
    P = (D1 * SENS / (2 ** 21) - OFF) / (2 ** 15)

    print(f"Temperature(MS5837): {TEMP / 100:.2f} °C")
    print(f"Pressure(MS5837): {P / 100:.2f} mbar")


def main():
    """ Main function to continuously read data from all sensors. """
    setup_i2c()
    setup_temperature_sensors()
    read_calibration_constants()

    while True:
        print("\n-----------------------")
        read_ds18b20()
        read_bme280()
        read_ms5837()
        print("-----------------------\n")
        #time.sleep(5)


# Run the main function
if __name__ == "__main__":
    main()
