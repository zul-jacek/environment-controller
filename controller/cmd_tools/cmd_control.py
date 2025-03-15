import argparse
from time import strftime
from controller.sensors.sensor_control import Sensors
from controller.power_management.ssr_control import SsrControl

def get_vpd(temperature, humidity):
    div = temperature - 0.5
    a = (610.7*10**(7.5*temperature/(temperature+237.3)))/1000
    b = (610.7*10**(7.5*div/(div+237.3)))/1000
    vpd = b - a*(humidity/100)
    return vpd

if __name__ == '__main__':
    parser = argparse.ArgumentParser("sensor values and actuator settings")
    sensor = Sensors()
    ssr_control = SsrControl()
    parser.add_argument("-img_1", "--get_cam01", help="get img from cam", action="store_true")
    parser.add_argument("--all", help="give you all informations", action="store_true")

    args = parser.parse_args()

    if args.get_cam01:
        sensor.take_photo()
    elif args.all:
        t_1, h_1 = sensor.get_dht20_data()
        t_2 = sensor.get_DS18B20_data()
        relais = ssr_control.get_relais_state()
        vpd = get_vpd(float(t_1), float(h_1))
        print(strftime("%Y-%m-%d %H:%M,"), f"T1={t_1}°C, H1={h_1}%, T2={t_2}°C, VPD {('%.2f' %(vpd))}, power_outlet {relais}")
    else:
        print("exit prog! for help type -h")
