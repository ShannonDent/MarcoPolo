from machine import Pin, I2C
from time import sleep
import onewire, ds18x20
import bme280

# Initialize I2C for BME280 (I2C1: scl=3, sda=4) and other sensors (I2C0: scl=1, sda=0)
i2c_bme = I2C(1, scl=Pin(3), sda=Pin(2))
i2c_other = I2C(0, scl=Pin(1), sda=Pin(0))

MS5837_ADDR = 0x77  # I2C address for MS5837
calibration_constants = []
devices_bme = i2c_bme.scan()
devices_other = i2c_other.scan()

print(f'I2C1 Devices (BME280): {devices_bme}')
print(f'I2C0 Devices (Other sensors): {devices_other}')

if not devices_bme:
    print("Warning: No BME280 detected! Check wiring.")
if not devices_other:
    print("Warning: No other I2C devices found! Check wiring.")

# Declare OneWire
one_wire_pin = Pin(15)
temperature_sensors = ds18x20.DS18X20(onewire.OneWire(one_wire_pin))

# Scan for DS18B20 devices
roms = temperature_sensors.scan()
#print('Found DS devices:', roms)
#print(f"Found {len(roms)} temperature sensors")

def BME_Data():
    try:
        bme = bme280.BME280(i2c=i2c_bme)  # BME280 object created
        print(f"\nPressure: {bme.values[1]}")
        print(f"Humidity: {bme.values[2]}")
    except Exception as e:
        print(f"BME280 Error: {e}")
        
        
def unpack(buffer):
    """ Unpacks MSB-ordered buffer of bytes into an unsigned integer. """
    return sum(byte << (i * 8) for i, byte in enumerate(reversed(buffer)))

def read_calibration_constants():
    """ Reads and unpacks calibration constants from the MS5837 sensor. """
    global calibration_constants
    registry_positions = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]
    
    try:
        cbytes = [i2c_other.readfrom_mem(MS5837_ADDR, reg, 2) for reg in registry_positions]
        calibration_constants = [unpack(cb) for cb in cbytes]
        print(f"Calibration Constants (MS5837): {calibration_constants}")
    except Exception as e:
        print(f"Error reading calibration constants: {e}")
        calibration_constants = []

def read_adc(command):
    """ Sends a command to the sensor and reads a 3-byte ADC value. """
    try:
        i2c_other.writeto(MS5837_ADDR, command)
        sleep(0.5)  # Wait for conversion
        return unpack(i2c_other.readfrom_mem(MS5837_ADDR, 0x00, 3))
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
    
    dt = D2 - calibration_constants[4] * (2 ** 8)
    TEMP = 2000 + dt * calibration_constants[5] / (2 ** 23)
    
    OFF = calibration_constants[1] * (2 ** 16) + (calibration_constants[3] * dt) / (2 ** 7)
    SENS = calibration_constants[0] * (2 ** 15) + (calibration_constants[2] * dt) / (2 ** 8)
    P = (D1 * SENS / (2 ** 21) - OFF) / (2 ** 15)
    
    print(f"Temperature (MS5837): {TEMP / 100:.2f} °C")
    print(f"Pressure (MS5837): {P / 100:.2f} mbar")

# Read calibration constants before entering the loop
read_calibration_constants()

def Temp_Data():
    temperature_sensors.convert_temp()  # Temperature to Celsius
    # Read and print temperature from each sensor
    for i, rom in enumerate(roms, start=1):
        tempC = temperature_sensors.read_temp(rom)
        print(f'Temp {i}: {tempC:.2f}°C')

while True:
    BME_Data()
    Temp_Data()
    read_ms5837()
    sleep(5)
