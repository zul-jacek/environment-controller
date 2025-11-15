import time
import threading
from controller.mqtt.mqtt_client import MqttCliet
import json
from queue import Queue

SEND_CYCLIC_TOPIC = "data"
CMD_RX_TOPIC = "cmd"

class MqttParser:
    """parser for mqtt"""

    def __init__(self, login):
        self.receiv_queue = Queue()
        self.mqtt = MqttCliet(self.receiv_queue)
        self.mqtt.add_subscriber(CMD_RX_TOPIC)
        self.mqtt.connect(*login)
        self.stop_event_cyclic_mqtt = threading.Event()
        self.send_cyclic_mqtt = threading.Thread(
            target=self.cyclic_mqtt_publish, daemon=True
        )

        self.mqtt_receiv_thread = threading.Thread(
            target=self.mqtt_receiv, daemon=True
        )
        self.repetition_cyclic_mqtt = 5
        self.ciclic_mqtt_callback = None

    def start_parser(self):
        # self.send_cyclic_mqtt.start()
        self.mqtt_receiv_thread.start()

    def mqtt_receiv(self):
        handlers = {
            "status": self.handle_status,
            "command": self.handle_command,
            "parameter": self.handle_parameter,
        }

        while True:
            time.sleep(0.1)
            if not self.receiv_queue.empty():
                data = self.receiv_queue.get()
                try:
                    data_dict = json.loads(data[1])
                except (json.JSONDecodeError, IndexError, TypeError):
                    data_dict = None

                if isinstance(data_dict, dict):
                    matched = False
                    keys = ["status", "command", "parameter"]

                    for key in keys:
                        if key in data_dict:
                            handlers[key](data_dict[key])
                            matched = True
                    for key, value in data_dict.items():
                        if key not in keys:
                            self.handle_unknown(key, value)

                    if not matched:
                        self.handle_no_match()
                else:
                    self.handle_no_json()

    def create_json_payload(self, data):
        payload = {"mqtt_msg": data}
        payload["mqtt_msg"]["time"] = time.strftime("%Y%m%d-%H:%M:%S")

        return json.dumps(payload)

    def cyclic_mqtt_publish(self):
        while not self.stop_event_cyclic_mqtt.is_set():
            time.sleep(self.repetition_cyclic_mqtt)
            if self.ciclic_mqtt_callback:
                payload ={"status": self.ciclic_mqtt_callback()}
            else:
                payload = {"error": "no data"}
            topic = SEND_CYCLIC_TOPIC
            data_to_send = self.create_json_payload(payload)
            self.mqtt.client.publish(topic, data_to_send)

    def handle_status(self, value):
        print(f"Handling status: {value}")

    def handle_command(self, value):
        print(f"Handling command: {value}")

    def handle_parameter(self, value):
        print(f"Handling parameter: {value}")

    def handle_unknown(self, key, value):
        print(f"Handling unknown: {key}")

    def handle_no_match(self):
        print("No relevant keys found.")

    def handle_no_json(self):
        print("no json")

    def __del__(self):
        pass




