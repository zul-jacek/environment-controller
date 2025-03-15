import time
from controller.power_management.ssr_control import SsrControl
import threading
from controller.mqtt.mqtt_client import MqttCliet
import json
from  json.decoder import JSONDecodeError
from controller.sensors.sensor_data_reader import DataReader
from queue import Queue
from controller.sensors.sensor_control import Sensors
from controller.control.time_control import TimeControl

SEND_CYCLIC_TOPIC = "data/box_01"
CMD_RX_TOPIC = "cmd"
CMD_TX_TOPIC = "cmd/response"


def create_json_payload(data):
    topic = SEND_CYCLIC_TOPIC
    payload = {"mqtt":{"sensors":{
        "idx_01":{
            "temperature":data[1],
            "humidity":data[2]
            },
        "idx_02":{
            "temperature_2":data[3]
            },
        "idx_03":{
            "relay_state":data[4]
            },
        "info":{
            "VPD":data[0]
        },
        }}}
    payload["mqtt"]["time"] = time.strftime("%Y%m%d-%H:%M:%S")
    
    return (topic, json.dumps(payload))

def cyclic_mqtt_publish(data_reader):
    while True:
        time.sleep(2)
        data = data_reader.get_all_data()
        payload = create_json_payload(data)
        mqtt.client.publish(*payload)

def control_vpd(data_reader, lower_limit, upper_limit):
    # very simple implementation. still needs to be optimized
    on_triggert = False
    off_triggert = False
    while True:
        time.sleep(0.5)
        vpd = data_reader.get_all_data()[0]
        if vpd < lower_limit:
            if not on_triggert:
                on_triggert = True
                off_triggert = False
                ssr_control.set_relais("xx1")
        if vpd > upper_limit:
            if not off_triggert:
                off_triggert = True
                on_triggert = False
                ssr_control.set_relais("xx0")

def time_control(name, pin, state):
    func_list = [
        0,
        1,
        switch_led(state)

    ]
    func_list[pin]

def switch_led(state):
    if state:
        ssr_control.set_relais("1xx")
    else:
        ssr_control.set_relais("0xx")

if __name__ == '__main__':
    time_list = [('led_1', 2, ('21:30', '21:31'))]
    login = [
        "90856c128b99426c847ba325322fc58c.s1.eu.hivemq.cloud",
        8883,
        "Jacek_01",
        "Xc82vbnm",
        ]
    receiv_queue = Queue()
    mqtt = MqttCliet(receiv_queue)
    mqtt.add_subscriber(CMD_RX_TOPIC)
    mqtt.connect(*login)
    ssr_control = SsrControl()
    sensors = Sensors()
    data_reader = DataReader(sensors, ssr_control)
    mqtt_updater_thread = threading.Thread(target=cyclic_mqtt_publish, args=[data_reader], daemon=True)
    mqtt_updater_thread.start()
    vpd_control_thread = threading.Thread(target=control_vpd, args=[data_reader, 0.9, 1.1], daemon=True)
    vpd_control_thread.start()
    # only for sym
    sensors.start_sensor_mock(data_reader)

    timer  = TimeControl(time_list, time_control)
    timer.start_timer()


    while True:
        time.sleep(0.1)
        # if not receiv_queue.empty():
        #     data = receiv_queue.get(timeout=5)
        #     try:
        #         data_dict = json.loads(data[1])
        #     except json.decoder.JSONDecodeError:
        #         data_dict = None
        #     if type(data_dict) == dict:
        #         try:
        #             print(data_dict["mqtt"]["sensors"])
        #         except Exception as e:
        #             print(f"scheiss{e}")

        #     else:
        #         print("no json")

      


