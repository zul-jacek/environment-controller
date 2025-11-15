from controller.mqtt.mqtt_parser import MqttParser

class Parser(MqttParser):
    """parser for mqtt"""

    def __init__(self, login):
        MqttParser.__init__(self, login)

    def handle_command(self, value):
        if isinstance(value, dict):
            payload = {}
            for key in value:
                if key == "broadcast_repetition_s":
                    self.repetition_cyclic_mqtt = int(value[key])
                    payload["success"] = {key:value[key]}
                else:
                    payload["faild"] = {key:"unknown command"}

        elif value == "help":
            payload ={"available commands":["broadcast_repetition_s"]}
        else:
            payload ={"faild":"need dict with commans"}
        data_to_send = self.create_json_payload(payload)
        self.mqtt.client.publish("cmd/response", data_to_send)
    
    def handle_unknown(self, key, value):
        payload ={"faild":{"value": value, "key":key}}
        data_to_send = self.create_json_payload(payload)
        self.mqtt.client.publish("cmd/response", data_to_send)

    def handle_no_match(self):
        payload ={"faild":{"key":"not available"}}
        data_to_send = self.create_json_payload(payload)
        self.mqtt.client.publish("cmd/response", data_to_send)

    def handle_no_json(self):
        payload ={"faild":{"json":"not parsable"}}
        data_to_send = self.create_json_payload(payload)
        self.mqtt.client.publish("cmd/response", data_to_send)
