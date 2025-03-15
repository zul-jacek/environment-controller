import time
import threading

 
class DataReader():
    def __init__(self, sensors, relays):
        self.data_list = [0, 0, 0, 0, "000"]
        self.sensor = sensors
        self.relay = relays
        self.sensor_data_updater_thread = threading.Thread(target=self._data_updater, daemon=True)
        self.sensor_data_updater_thread.start()
        
    def _calc_vpd(self, temperature, humidity):
        div = temperature - 0.5
        a = (610.7*10**(7.5*temperature/(temperature+237.3)))/1000
        b = (610.7*10**(7.5*div/(div+237.3)))/1000
        vpd = b - a*(humidity/100)
        
        return vpd

    def _data_updater(self):
        while True:
            temp, humidity = self.sensor.get_dht20_data()
            vpd = self._calc_vpd(float(temp),float(humidity))
            state = self.relay.get_relais_state()
            temp_2 = self.sensor.get_DS18B20_data()
            self.data_list = [vpd, temp, humidity,temp_2, state]

    def get_temperature(self):

        return self.data_list[1]

    def get_temperature_2(self):

        return self.data_list[3]
    
    def get_humidity(self):
        
        return self.data_list[2]

    def get_vpd(self):
        
        return self.data_list[0]

    def get_relay_state(self):
        
        return self.data_list[4]
    
    def get_all_data(self):

        return self.data_list

if __name__ == '__main__':
    control = DataReader()
    while True:
        time.sleep(5)
        print(control.get_vpd())
