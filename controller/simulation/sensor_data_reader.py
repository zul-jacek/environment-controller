import time
import threading
import math

 
class DataReaderSim:
    def __init__(self, relay):
        self.relay = relay
        self.data_list = [0, 0, 0, 0, "000"]
        self.sensor_data_updater_thread = threading.Thread(target=self._data_updater, daemon=True)
        self.sensor_data_updater_thread.start()
        
    def _calc_vpd(self, temperature, humidity):
        div = temperature - 0.5
        a = (610.7*10**(7.5*temperature/(temperature+237.3)))/1000
        b = (610.7*10**(7.5*div/(div+237.3)))/1000
        vpd = b - a*(humidity/100)
        
        return vpd

    def _calc_absolute_humidity(self, temp_c, rel_humidity):
        """
        Berechnet absolute Feuchte in g/m³
        Formel aus Meteorologie:
        ρ_abs = 216.7 * e / (T + 273.15)
        e = 6.112 * exp((17.62*T)/(243.12+T)) * RH/100
        """
        e = 6.112 * math.exp((17.62 * temp_c) / (243.12 + temp_c)) * rel_humidity / 100.0
        abs_h = 216.7 * e / (temp_c + 273.15)
        return abs_h

    def _data_updater(self):
        self.temp, self.humidity = 23, 55
        while True:
            fan = self.data_list[4][0]
            humidifier = self.data_list[4][1]
            lamp = self.data_list[4][2]
            if (fan == "1") and (self.humidity>40):
                self.humidity -= 0.03
                if self.temp > 22:
                    self.temp -= 0.0005
            if (fan != "1") and (self.humidity<85):
                self.humidity += 0.008
                if self.temp < 22:
                    self.temp += 0.0002
            if (humidifier == "1") and (self.humidity<85):
                self.humidity += 0.05

            vpd = self._calc_vpd(float(self.temp), float(self.humidity))
            state = self.relay.get_relais_state()
            temp_2 = self._calc_absolute_humidity(self.temp, self.humidity)
            self.data_list = [vpd, self.temp, self.humidity, temp_2, state]
            time.sleep(0.5)

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


