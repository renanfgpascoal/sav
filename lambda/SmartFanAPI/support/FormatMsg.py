import json, uuid


class FormatMsg():
    def build(data: dict) -> str:
        def add_meta(data: dict) -> dict:
            if ("trans_uuid" in data):
                return data
            
            meta = {"trans_uuid" : str(uuid.uuid4())}
            meta.update(data)

            return meta
        
        payload = add_meta(data)
        built = json.dumps(payload)
        if (type(built) != str):
            return {}

        return {"trans_uuid": payload["trans_uuid"], "built": built}
    
    def parse(msg: str) -> dict:
        parsed = json.loads(msg)
        if (type(parsed) != dict):
            return {}
        if ("trans_uuid" not in parsed):
            return {}
        return parsed