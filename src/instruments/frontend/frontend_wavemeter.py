from typing import Any
import paho.mqtt.client as mqtt


class MqttWavemeter:

    wavelength_value = 0.0
    client = None
    mqtt_path = ''


    def __init__(self, resource_string: str):
        self.mqtt_path = resource_string
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def open(self):
        self.client.connect(host="fys-s-dep-bkr01.fysad.fys.kuleuven.be")
        self.client.loop_start()
    
    def on_connect(self,client: mqtt.Client, userdata, flags, rc, bla):
        client.subscribe(self.mqtt_path)
        print('subscribed to '+str(self.mqtt_path))

    def on_message(self,client: mqtt.Client,userdata: Any,message: mqtt.MQTTMessage,):
        timestamp, value = [float(f) for f in message.payload.decode()[1:-1].split(", ")]
        # print('MQTT: '+str(value))
        if value>0:
            self.frequency_value = value
            

    def getdata(self):
        return self.frequency_value
    
    def set_setpoint(self):
        pass
        
   
if __name__ == "__main__":
    wm = MqttWavemeter('HFWM/8731/frequency/1')
    wm.open()
    while True:
        continue


