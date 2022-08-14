from .AppComm import AppComm


class AppCmd():
    def __do_transaction(self, client: AppComm, route: str, req: dict) -> bool:
        status = True
        # Sending request
        trans_id = client.transmit_msg(req, route)
        if (trans_id == ""):
            status = False
        
        # Listening for response
        # res = client.track_msg(trans_id, route, 1)
        # if (res == {}):
        #     return False
        
        return status
    
    def set_fan_pwr(self, client: AppComm, route: str, dev_id: str, pwr: int):
        req = {
            "dev_id": dev_id,
            "op_id": 0,
            "fan_speed": pwr
        }
        
        return self.__do_transaction(client, route, req)

    def turn_on(self, client: AppComm, route: str, dev_id: str):
        req = {
            "dev_id": dev_id,
            "op_id": 0,
            "fan_speed": 10
        }
        
        return self.__do_transaction(client, route, req)

    def turn_off(self, client: AppComm, route: str, dev_id: str):
        req = {
            "dev_id": dev_id,
            "op_id": 0,
            "fan_speed": 0
        }
        
        return self.__do_transaction(client, route, req)
