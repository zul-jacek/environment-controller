import RPi.GPIO as GPIO
from controller.drivers.DHT20_driver import DHT20
import os
from time import strftime
import time

I2C_BUS: int     = 0x01  # bus address
I2C_ADDRESS: int = 0x38  # default DHT2x I2C device address 

class Sensors():
    
    def __init__(self):
        self.dht20 = DHT20(I2C_BUS, I2C_ADDRESS)

    def load(self, file):
        with open(file, 'r') as file:
            return file.read()
    
    def get_dht20_data(self):
        not_execute = True
        count = 0
        while (count < 3) and not_execute:
            try:
                count += 1
                if not self.dht20.begin():
                    raise RuntimeError("DHT2x sensor initialization failed")
                else:
                    t_celcius, humidity, crc_error = self.dht20.get_temperature_and_humidity()
                    t_celcius = ("%.2f" %(t_celcius))
                    humidity = ("%.2f" %humidity)
                not_execute = False
            except Exception as e:
                print(f"retry read dat \n {e}")
                time.sleep(1.1)
        if not_execute:
            raise SystemError("can not read data!")

        return t_celcius, humidity

    def get_DS18B20_data(self):
        not_execute = True
        count = 0
        while (count < 3) and not_execute:
            try:
                count += 1
                f = os.path.join('/sys/bus/w1/devices/28-000005238c2f', "w1_slave")
                temp_str = str(self.load(f))
                temp_str = temp_str[-6:-4]+ "." +temp_str[-4:-2]
                t_zwei = temp_str
                not_execute = False
            except Exception as e:
                print(f"retry read dat \n {e}")
                time.sleep(1.1)
        if not_execute:
            raise SystemError("can not read data!")

        return t_zwei

    def take_photo(self):
        # print("\n")
        time_str = strftime("%Y%m%d_%H%M")
        file_name = r"/home/admin/python_test_code/" + f"{time_str}" + ".jpg"
        cmd = r"fswebcam -r 640x480 --no-banner " + file_name + r"> /dev/null 2>&1"
        os.system(cmd)
        # print("\n")
        print(f"Writing JPEG image to {file_name}")

if __name__ == '__main__':
    sensor = Sensors()
    print(sensor.get_dht20_data())
    print(sensor.get_DS18B20_data())
    sensor.take_photo()



