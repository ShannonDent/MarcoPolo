from tuppersat.radio.Temperature import Temperature
from tuppersat.radio.Pressure import Pressure
from Housekeeping_sensors.GPS2 import GPS
from SD import sd_card
from tuppersat.radio.radio_class import Radio
import time
from Sensor_code.UV import UV
from Sensor_code.O3 import OzoneSensor


def setup(sensors):
    for sensor in sensors:
        sensor.setup()


def write_housekeeping(sensors_housekeeping, housekeeping_data):
    sensor_data = []
    for sensor in sensors_housekeeping:
        sensor.read_data()
        sensor_data.append(sensor.data)

    if sensor_data[0] is not None and sensor_data[0][1] != '':
        #print(sensor_data)
        housekeeping_data["hhmmss"] = (sensor_data[0][3])
        housekeeping_data["latitude"] = (float(sensor_data[0][0]))
        housekeeping_data["longitude"] = (float(sensor_data[0][1]))
        housekeeping_data["hdop"] = (float(sensor_data[0][4]))
        housekeeping_data["altitude"] = (float(sensor_data[0][2]))
        housekeeping_data["ext_temp"] = 23.11 #(float(sensor_data[1]))
        housekeeping_data["int_temp"] = (float(sensor_data[1])) #(float(sensor_data[2]))
        housekeeping_data["Pressure"] = (float(sensor_data[2]))

    return housekeeping_data


def write_payload(sensors_payload, payload_data):
    sensor_data = []
    for sensor in sensors_payload:
        sensor.read_data()
        sensor_data.append(sensor.data)

    if sensor_data[0] is not None and sensor_data[0][1] != '':
        #print(sensor_data)
        payload_data["hhmmss"] = (str(112211.111))
        payload_data["UVA"] = (float(sensor_data[0][0]))
        payload_data["UVB"] = (float(sensor_data[0][1]))
        payload_data["UVC"] = (float(sensor_data[0][2]))
        payload_data["Ozone"] = (float(sensor_data[1]))
        payload_data["Temp"] = (float(sensor_data[0][3]))

    return payload_data


def main():

    ds_pin_ext = 22
    ds_pin_int = 14
    sensors_housekeeping = [GPS(), Temperature(ds_pin_int), Pressure()] #Temperature(ds_pin_ext) #Pressure()
    sensors_payload = [UV(), OzoneSensor(28, 27)] 
    sd = sd_card()

    housekeeping_data = {"hhmmss": None, "latitude": None, "longitude": None,
                         "altitude": None, "hdop": None, "int_temp": None,
                         "ext_temp": None, "Pressure": None}
    payload_data = {"hhmmss": None, "UVA": None, "UVB": None,
                    "UVC": None, "Ozone": None, "Temp": None}

    payload_keys = ["hhmmss", "UVA", "UVB", "UVC", "Ozone", "Temp"]
    housekeeping_keys = ["hhmmss", "latitude", "longitude",
                         "altitude", "hdop", "int_temp", "ext_temp", "Pressure"]

    setup(sensors_housekeeping)
    setup(sensors_payload)
    sd.setup()
    radio = Radio()
    oldtimehk = time.time()
    oldtimepl = time.time()
    try:
        while True:
            house_data = write_housekeeping(
                sensors_housekeeping, housekeeping_data)
            pay_data = write_payload(sensors_payload, payload_data)
            pay_data["hhmmss"] = house_data["hhmmss"]

            if pay_data['UVA'] is not None:
                sd.write_payload(pay_data, payload_keys)
                #print(pay_data)
                if time.time() - oldtimepl >= 20:
                    #radio = Radio()
                    radio.run(pay_data)
                    oldtimepl = time.time()
                    

            if house_data['latitude'] is not None:
                sd.write_housekeeping(house_data, housekeeping_keys)
                #print(house_data)
                if time.time() - oldtimehk >= 10:
                    #radio = Radio()
                    radio.run(house_data)
                    oldtimehk = time.time()
                
    finally:
        sd.teardown()  # teardown function to clean up the SD card
        print('done')


if __name__ == "__main__":
    main()
