import machine
import time


class OzoneSensor:
    def __init__(self, pin_vgas, pin_vgas0):
        self.potentiometer = machine.ADC(pin_vgas)
        self.potentiometer0 = machine.ADC(pin_vgas0)
        self.SENSITIVITY_CODE = -51.7
        self.TIA_GAIN = 499
        self.conversion_factor = 3.3 / 65535
        self.M = self.SENSITIVITY_CODE * \
            self.TIA_GAIN * (10 ** (-9)) * (10 ** 3)
        self.data = None

    def setup(self):
        try:
            #self.scan_devices()
            print("Ozone sensor is setup...")
        except:
            print("Ozone sensor is not connected....")

    def read_data(self):
        try:
            vgas =0
            vgas0=0
            vgas = self.potentiometer.read_u16() * self.conversion_factor
            vgas0 = self.potentiometer0.read_u16() * self.conversion_factor
            v_real = vgas - vgas0
            self.data = (1 / self.M) * v_real
        except:
            print("Ozone is disconnected....")


def main():
    ozone_sensor = OzoneSensor(28, 27)
    ozone_sensor.setup()

    while True:
        ozone_sensor.read_data()
        ozone_concentration = ozone_sensor.data
        print(f"Ozone Concentration: {ozone_concentration}")
        time.sleep(1)


if __name__ == "__main__":
    main()
