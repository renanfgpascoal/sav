from paho.mqtt import client as mqtt_client
from timeout_timer import timeout, TimeoutInterrupt
import time, ssl, os

EN_PRINT_DEBUG = False

class MqttClient:
    def __init__(self, cfg):
        self.__broker = cfg["broker"]
        self.__port = cfg["port"]
        self.__client_id = cfg["client_id"]
        self.__username = cfg["username"]
        self.__password = cfg["password"]
        self.__cert_path = cfg["cert_path"]
        self.__qos = cfg["qos"]
        self.__client = mqtt_client.Client(self.__client_id)
        self.__recv_message = []
        
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, self.__cert_path)
        self.__client.tls_set(abs_file_path, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.__client.tls_insecure_set(True)

    def __connect(self, timeout_s = 10):
        def on_log(client, userdata, level, buf):
            global EN_PRINT_DEBUG
            if (EN_PRINT_DEBUG == False):
                return
            
            print(buf)
            return
        
        def on_connect(client, userdata, flags, rc):
            if (rc == 0):
                return
            else:
                print("Failed to connect, return code {}\n".format(rc))
                return
            
        self.__client.on_log = on_log
        self.__client.username_pw_set(self.__username, self.__password)
        self.__client.on_connect = on_connect
        
        try:
            with timeout(timeout_s, "thread"):
                ret = self.__client.connect(self.__broker, self.__port)

                if (ret != 0):
                    raise Exception(ret)

                while (self.__client.is_connected == False):
                    time.sleep(0.100)

        except Exception:
            pass

        return self.__client.is_connected

    def subscribe(self, topic, timeout_s):
        def on_message(client, userdata, msg):
            self.__recv_message.append(msg.payload.decode())

        if (self.__connect() == False):
            print("Subscribe fail: disconnected from broker")
            return []
        try:
            ret = self.__client.subscribe(topic, self.__qos)
        except Exception:
            pass

        if (ret[0] != 0):
            return []

        self.__client.on_message = on_message
        
        try:
            with timeout(timeout_s, "thread"):
                self.__client.loop_forever(timeout_s)
        except TimeoutInterrupt:
            self.__client.disconnect()
        
        return self.__recv_message

    def publish(self, message, topic):
        if (self.__connect() == False):
            print("Publish fail: disconnected from broker")
            return False
        try:
            result = self.__client.publish(topic, message, self.__qos)
        except Exception:
            pass
        
        self.__client.loop_start()
        
        status = False
        if (result[0] == 0):
            status = True
        else:
            print("Failed to send message to topic {}".format(topic))
            status = False
        
        self.__client.loop_stop()
        self.__client.disconnect()

        return status

def create_clients(numOfClients):
    import random

    cfg = {
        "broker": "mqtt.flespi.io",
        "port": 8883,
        "username": "FlespiToken eoKrlkh5WvNs8iGlvmjJFzTKmDMK3Cq8R0n09uVTOz9MFFXYR4xnthVEIvcBYqzD",
        "password": "",
        "cert_path": "certs/mqtt_flespi_io.pem",
        "qos": 1
    }

    c = []
    for n in range(0, numOfClients):
        cfg["client_id"] = "python-mqtt-{}".format(random.randint(0, 1000))
        c.append(MqttClient(cfg))
        
    return c

def tx_thread(queue, type, client, data, topic):
    time.sleep(1)
    r = ""

    if (type == 0):
        r = client.publish(data, topic)
    if (type == 1 | type == 2):
        r = client.publish_json(data, topic)
        
    return queue.put(r)

def rx_thread(queue, type, client, topic):
    r = ""
    
    if (type == 0 | type == 1 | type == 2):
        r = client.subscribe(topic, 3)

    return queue.put(r)

def do_tx(type, data, topic):
    import threading, queue

    c = create_clients(2)
    if (len(c) < 2):
        return

    q = queue.SimpleQueue()
    t = []
    t.append(threading.Thread(target = rx_thread, args = [q, type, c[0], topic]))
    t.append(threading.Thread(target = tx_thread, args = [q, type, c[1], data, topic]))

    for th in t:
        th.start()

    ret = []
    for i in range(0, 2):
        r = q.get()
        ret.append(r)
    
    return ret

def tx_test(topic):
    print("Running TX Test...")
    data = "test"
    ret = do_tx(0, data, topic)

    if ((ret[0] == False) | (len(ret[1]) == 0)):
        return "Failed"

    rx_msg = ret[1]
    return "Pass" if (rx_msg[0] == data) else "Failed"

if (__name__ == "__main__"):
    topic = "/topic/test"
    print(tx_test(topic))