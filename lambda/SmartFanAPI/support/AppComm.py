from .MqttClient import MqttClient
from .FormatMsg import FormatMsg


class AppComm():
    def __init__(self, cfg: dict) -> None:
        self.__client = MqttClient(cfg)
        
    def __receive(self, route: str, timeout_s: int) -> list:
        return self.__client.subscribe(route, timeout_s)
    
    def __transmit(self, package: str, route: str) -> bool:
        return self.__client.publish(package, route)
    
    def track_msg(self, trans_id: str, route: str, timeout_s: int) -> dict:
        received = self.__receive(route, timeout_s)
        for r in received:
            parsed = FormatMsg.parse(r)
            if ((parsed == {}) | (parsed["transaction_uuid"] != trans_id)):
                continue
            return parsed

        return {}
        
    def transmit_msg(self, data: dict, route: str) -> str:
        msg = FormatMsg.build(data)
        if (msg == {}):
            return ""
        
        if (self.__transmit(msg["built"], route) == False):
            return ""
        
        return msg["trans_uuid"]
    
def create_clients(numOfClients) -> list:
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
        c.append(AppComm(cfg))
        
    return c

def tx_thread(queue, type, client, data, route) -> any:
    import time
    
    time.sleep(1)
    r = ""

    if (type == 0):
        r = client.transmit_msg(data, route)
    if (type == 1):
        payload = {"transaction_uuid": "teste"}
        payload.update(data)
        r = client.transmit_msg(payload, route)
        
    return queue.put(r)

def rx_thread(queue, type, client, route):
    r = ""
    
    if (type == 0):
        r = client._AppComm__receive(route, 3)
    if (type == 1):
        r = client.track_msg("teste", route, 3)

    return queue.put(r)

def do_tx(type, data, route) -> list:
    import threading, queue, time

    c = create_clients(2)
    if (len(c) < 2):
        return []

    q = queue.SimpleQueue()
    t = []
    t.append(threading.Thread(target = rx_thread, args = [q, type, c[0], route]))
    t.append(threading.Thread(target = tx_thread, args = [q, type, c[1], data, route]))

    for th in t:
        th.start()

    time.sleep(1)
    ret = []
    for i in range(0, 2):
        # May have race condition
        r = q.get(timeout = 5)
        ret.append(r)
    
    return ret

def track_msg_test(topic) -> str:
    print("Running Track Message Test...")
    data = {"payload": "test"}
    ret = do_tx(1, data, topic)

    if ((ret[0] == "") | (len(ret[1]) == 0)):
        return "Failed"
    
    rx_msg = ret[0]
    return "Pass" if (rx_msg == "teste") else "Failed"

def transmit_msg_test(route) -> str:
    import json
    
    
    print("Running Transmit Message Test...")
    data = {"payload": "test"}
    ret = do_tx(0, data, route)

    if ((ret[0] == "") | (len(ret[1]) == 0)):
        return "Failed"

    tx_msg = ret[0]
    rx_msg = json.loads(ret[1][0])

    return "Pass" if (rx_msg["transaction_uuid"] == tx_msg) else "Failed"

if (__name__ == "__main__"):
    route = "/topic/test"
    print(track_msg_test(route))
    print(transmit_msg_test(route))