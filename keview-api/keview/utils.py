import json
import random
import numpy as np

from tensorflow.python import keras


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


class MNIST:

    @staticmethod
    def get_test_image():
        data = keras.datasets.mnist
        (_, _), (test_images_temp, _) = data.load_data()
        test_images = test_images_temp / 255.0
        test_images = test_images.reshape(10000, 28, 28, 1)

        image_index = random.randint(0, len(test_images))
        return test_images[image_index]
