import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

class MqttCliet():
    def __init__(self, queue = None):
        self.subscribtion = []
        self.receiv_queue = queue
        self.init_client()

    def init_client(self):
        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        # attach callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self, host, port, user, password, tls=True):
        self.client.tls_set()
        self.client.tls_insecure_set(True)
        self.client.username_pw_set(user, password=password)
        self.client.connect(host, port=port)
        self.client.loop_start()

    def suspend(self):
        self.client.loop_stop()

    def resume(self):
        self.client.loop_start()

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

    def add_subscriber(self, subscriber):
        self.subscribtion.append((subscriber,0))

    def on_connect(self, client, userdata, flags, rc, properties):
        print("Connected with result code: " + str(rc))
        # default subscribtion
        if self.subscribtion:
            self.client.subscribe(self.subscribtion)

    def on_message(self, client, userdata, message):
        if self.receiv_queue:
            self.receiv_queue.put((message.topic, message.payload))
