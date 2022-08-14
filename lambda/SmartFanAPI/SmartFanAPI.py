from .support.AppComm import AppComm
from .support.AppCmd import AppCmd
import os

class SmartFanAPI:
    def __init__(self, cfg_path: str) -> None:
        cfg = self.__parse_config(cfg_path)
        self.__comm = AppComm(cfg)
        self.__route_op = cfg["topic_op"]
        self.__cmd = AppCmd()
    
    def __build_config(self) -> dict:
        with open("default_config.txt", "w") as f:
            f.write("BROKER=\n")
            f.write("PORT=\n")
            f.write("CLIENT_ID=\n")
            f.write("USERNAME=\n")
            f.write("PASSWORD=\n")
            f.write("CERT_PATH=\n")
            f.write("TOPIC_OP=\n")

        return {}

    def __parse_config(self, file: str) -> dict:
        lines, cfg = "", {}
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, file)
        try:
            with open(abs_file_path, "r") as f:
                lines = f.readlines()
        except OSError:
            return self.__build_config()

        for line in lines:
            if line.startswith('BROKER='):
                cfg['broker'] = line[len('BROKER='):-1]
            if line.startswith('PORT='):
                cfg['port'] = int(line[len('PORT='):-1])
            if line.startswith('CLIENT_ID='):
                cfg['client_id'] = line[len('CLIENT_ID='):-1]
            if line.startswith('USERNAME='):
                cfg['username']= line[len('USERNAME='):-1]
            if line.startswith('PASSWORD='):
                cfg['password'] = line[len('PASSWORD='):-1]
            if line.startswith('CERT_PATH='):
                cfg['cert_path'] = line[len('CERT_PATH='):-1]
            if line.startswith('QOS='):
                cfg['qos'] = int(line[len('QOS='):-1])
            if line.startswith('TOPIC_OP='):
                cfg['topic_op'] = line[len('TOPIC_OP='):-1]
        
        return cfg
    
    def set_fan_pwr(self, pwr: int, dev_id: str) -> bool:
        return self.__cmd.set_fan_pwr(self.__comm, self.__route_op, dev_id, pwr)
        
    def turn_on(self, dev_id: str) -> bool:
        return self.__cmd.turn_on(self.__comm, self.__route_op, dev_id)
        
    def turn_off(self, dev_id: str) -> bool:
        return self.__cmd.turn_off(self.__comm, self.__route_op, dev_id)
    
def set_fan_pwr_tests():
    import random
    
    
    print("Running Set Fan Power Tests")
    
    app = SmartFanAPI("config.txt")
    return app.set_fan_pwr(50, "0A0D")
    
if (__name__ == "__main__"):
    print(set_fan_pwr_tests())