import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.float32):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

    @staticmethod
    def encodeJSON(dict: dict):
        dump = json.dumps(dict, cls=NumpyEncoder)
        return json.loads(dump)
