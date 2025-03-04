import machine
import time


class Pressure:
    def __init__(self):
        self.sclpin = machine.Pin(13)
        self.sdapin = machine.Pin(12)
        self.registry_positions = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]
        self.data = []
        self.d1 = 0
        self.d2 = 0
        self.cbytes = []
        self.temp = []

    def scan_devices(self):
        devices = self.i2c.scan()
        print(devices)

    def unpack(self, buffer):
        _buffer = reversed(bytearray(buffer))
        return sum(_byte << (_i * 8) for _i, _byte in enumerate(_buffer))

    def read_constants(self):
        cbytes_ = [self.i2c.readfrom_mem(119, poss, 2)
                   for poss in self.registry_positions]
        self.cbytes = [self.unpack(constant) for constant in cbytes_]

    def setup(self):
        self.i2c = machine.I2C(0, scl=self.sclpin, sda=self.sdapin)
        self.scan_devices()
        self.read_constants()
        print("Pressure Sensor is setup...")

    def read_data(self):
        TEMPERATURE_ADC = b'\x48'
        PRESSURE_ADC = b'\x58'
        self.i2c.writeto(119, TEMPERATURE_ADC)
        time.sleep_ms(500)
        t_adc_bytes = self.i2c.readfrom_mem(119, 0x00, 3)

        self.i2c.writeto(119, PRESSURE_ADC)
        time.sleep_ms(500)
        P_adc_bytes = self.i2c.readfrom_mem(119, 0x00, 3)
        self.d2 = self.unpack(t_adc_bytes)
        self.d1 = self.unpack(P_adc_bytes)
        self.calculate_temperature()
        self.calculate_pressure()

    def calculate_temperature(self):
        dt = self.d2 - self.cbytes[4] * (2 ** 8)
        TEMP = 2000 + dt * self.cbytes[5] / (2 ** 23)
        self.temp = TEMP

    def calculate_pressure(self):
        dt = self.d2 - self.cbytes[4] * (2 ** 8)
        OFF = self.cbytes[1] * (2 ** 16) + (self.cbytes[3] * dt) / (2 ** 7)
        SENS = self.cbytes[0] * (2 ** 15) + (self.cbytes[2] * dt) / (2 ** 8)
        P = (self.d1 * SENS / (2 ** 21) - OFF) / (2 ** 15)
        self.data = P


def main():
    pressure = Pressure()
    pressure.setup()

    while True:
        pressure.read_data()
        print(f'Measured pressure is {pressure.data / 100 :2.2f} millibars')


if __name__ == "__main__":
    main()