from machine import Pin, I2C 
from time import sleep
import onewire, ds18x20
import bme280       


i2c = machine.I2C(0 ,scl = machine.Pin(1), sda = machine.Pin (0))
devices = i2c.scan()
print(f'I2C Devices Found: {devices}')


# Declare OneWire
one_wire_pin = machine.Pin(15)
temperature_sensors = ds18x20.DS18X20(onewire.OneWire(one_wire_pin))

    # Scan for DS18B20 devices
roms = temperature_sensors.scan()
    #print('Found DS devices:', roms)
    #print(f"Found {len(roms)} temperaure sensors")

def BME_Data():
    bme = bme280.BME280(i2c=i2c)          #BME280 object created
    print(f"\nPressure: {bme.values[1]}")
    print(f"Humidity: {bme.values[2]}")
    
    #return bme.values[1], bme.values[2]

def Temp_Data():
    temperature_sensors.convert_temp()  # Temperature to Celsius
    # Read and print temperature from each sensor
    #for rom in roms:
    for i, rom in enumerate(roms, start=1):
        tempC = temperature_sensors.read_temp(rom)
        print(f'Temp {i}: {tempC:.2f}°C')


while True:
    BME_Data()
    Temp_Data()


    sleep(5)