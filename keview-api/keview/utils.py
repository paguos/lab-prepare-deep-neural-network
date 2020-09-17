import json
import inflection
import matplotlib.pyplot as plt
import numpy as np
import random
import shutil
import time
from PIL import Image
from os import listdir
from os.path import isfile, join

from loguru import logger
from pathlib import Path
from tensorflow.python import keras

from keview.models import DenseLayer
from keview.models import FlattenLayer
from keview.models import KerasModel


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

    @staticmethod
    def save_images(model: KerasModel, input_img):
        img_directory = "assets/images/-1/"
        shutil.rmtree(img_directory, ignore_errors=True)
        Path(img_directory).mkdir(parents=True, exist_ok=True)
        input_img = np.reshape(input_img*255, (28, 28))
        plt.imsave(f"{img_directory}input_{str(time.time())}.png",
                   Image.fromarray(input_img))

        layer_index = 0

        for layer in model.get_layers():
            comp_index = 0
            layer_name = inflection.underscore(type(layer).__name__)

            logger.info(f"Processing layer {layer_name} ...")
            if isinstance(layer, DenseLayer):
                continue
            if isinstance(layer, FlattenLayer):
                continue
            img_directory = f"assets/images/{layer_index}"
            shutil.rmtree(img_directory, ignore_errors=True)
            Path(img_directory).mkdir(parents=True, exist_ok=True)

            for component in layer.get_components():
                output = component.get_output()
                plt.imsave(
                    f"{img_directory}/{layer_name}_{comp_index}__{str(time.time())}.png", output
                )
                comp_index += 1

            layer_index += 1

    @staticmethod
    def list_images(layer_id: int):
        img_path = f"assets/images/{layer_id}"
        return [f for f in listdir(img_path) if isfile(join(img_path, f))]
