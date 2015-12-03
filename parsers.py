import json

class JSONParser:

    @staticmethod
    def dump(python_object):
        if python_object:
            return bytes(json.dumps(python_object), encoding='utf-8')
        return None

    @staticmethod
    def load(response):
        return json.loads(response.read().decode('utf-8'))

class RAWParser:

    @staticmethod
    def dump(python_object):
        return python_object

    @staticmethod
    def load(response):
        return response