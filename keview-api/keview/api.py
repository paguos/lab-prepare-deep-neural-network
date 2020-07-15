from PIL import Image
import io
from flask import Flask

from nnv import NNV
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException, Request
from fastapi import File, UploadFile
from keras.preprocessing.image import img_to_array
from loguru import logger
from tensorflow.python import keras

import numpy as np

from keview.models import KerasModel, Layer
from keview.utils import NumpyEncoder

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



""" ----------------------------------- """
data = keras.datasets.mnist
(train_images_temp, train_labels), (test_images_temp, test_labels) = data.load_data()
train_images = train_images_temp / 255.0

logger.info(f"Test Images Shape: {np.shape(train_images)}")
test_images = test_images_temp / 255.0
train_images = train_images.reshape(60000, 28, 28, 1)
test_images = test_images.reshape(10000, 28, 28, 1)
image = 23
""" ----------------------------------- """

logger.info("Loading model ...")
model = keras.models.load_model("examples/test.h5")
keras_model = KerasModel(model)
logger.info("Loading model ... done!")


plt.imshow(test_images_temp[image], cmap='binary')
keras_model.run(test_images[image])


app = FastAPI()

# https://fastapi.tiangolo.com/advanced/templates/
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/visualization/summary")
async def visualization():
    # show the summary of model
    return model.summary()


"""------------------------------------------------------------------------------------------------------------------------- """

@app.get("/keview/v1alpha/layers")
async def layers():
    layers = keras_model.get_layers()
    #plot_model(model, to_file='model.png')

    layers_data = []
    index = 0
    for layer in layers:
        layer_data = layer.toJSON()
        layer_data["id"] = index
        layers_data.append(layer_data)
        index += 1

    return {"layers": layers_data}




@app.get("/keview/v1alpha/layers/{layer_id}")
async def layer(request: Request, layer_id: str):
    layer = fetch_layer(keras_model, layer_id)
    layer_data = layer.toJSON()
    layer_data["id"] = layer_id

    # case conv2d layer
    if layer_id == "0" or layer_id == "3":
        featuremap = keras_model.get_layers()[int(layer_id)].get_featuremaps()[-1]
        output = featuremap.get_output()
        plt.imshow(output, cmap="binary")
        #plt.show()
        plt.imsave('../keview-api/static/images/tmp/tmp_conv2d.png', output)

        bias = featuremap.get_bias()
        weights = featuremap.get_weights()

        print(f"bias: {bias}")
        print(f"weights: {weights}")

        return templates.TemplateResponse("conv2d_layer.html", {"request": request, "bias": bias, "weights": weights, "output": output})

    # case batch_normalization_layer
    elif layer_id == "1" or layer_id == "4":
        batch_normalization_layer = keras_model.get_layers()[int(layer_id)].get_normalization_dimensions()
        for i in range(len(batch_normalization_layer)):
            # is None
            output = batch_normalization_layer[i].get_output()
            plt.imshow(output, cmap="binary")
            #plt.show()
            plt.savefig('../keview-api/static/images/tmp/tmp_batch_normalization_' + str(i) + '.png')

            beta = batch_normalization_layer[i].get_beta()
            gamma = batch_normalization_layer[i].get_gamma()
            mean = batch_normalization_layer[i].get_mean()
            variance = batch_normalization_layer[i].get_variance()

        return templates.TemplateResponse("batch_normalization_layer.html", {"request": request, "beta": beta, "mean": mean, "gamma": gamma, "variance": variance, "output": output})

    # case max_pooling2d layer
    elif layer_id == "2" or layer_id == "5":
        max_pooling_dim = keras_model.get_layers()[int(layer_id)].get_max_pooling_dimensions()
        for i in range(len(max_pooling_dim)):
            output = max_pooling_dim[i].get_output()
            plt.imshow(output, cmap="binary")
            #plt.show()
            plt.savefig('../keview-api/static/images/tmp/tmp_max_pooling_' + str(i) + '.png')

        return templates.TemplateResponse("max_pooling_layer.html", {"request": request, "output": output})

    # flatten layer
    elif layer_id == "6":
        return templates.TemplateResponse("flatten_layer.html", {"request": request})

    # dense layer
    elif layer_id == "7" or layer_id == "8":
        neurons = keras_model.get_layers()[int(layer_id)].get_neurons()
        neuron_list = []

        for i in range(len(neurons)):
            tmp = []
            tmp.append(neurons[i].get_weights())
            tmp.append(neurons[i].get_bias())
            neuron_list.append(tmp)

        return templates.TemplateResponse("dense_layer.html", {"request": request, "neurons": neuron_list})

    else:
        print("ERROR: Invalid Layer ID! Choose an ID in range [0, 8].")

    #return layer_data





@app.get("/keview/v1alpha/layers/{layer_id}/components")
async def components(layer_id):
    layer = fetch_layer(keras_model, layer_id)
    components = [c.toJSON() for c in layer.get_components()]
    return NumpyEncoder.encodeJSON(components)


@app.get("/keview/v1alpha/layers/{layer_id}/components/{component_id}")
async def component(layer_id, component_id):
    layer = fetch_layer(keras_model, layer_id)
    component = fetch_component(layer, component_id)
    return NumpyEncoder.encodeJSON(component.toJSON())


@app.get("/keview/v1alpha/layers/{layer_id}/outputs")
async def outputs(layer_id):
    layer = fetch_layer(keras_model, layer_id)
    outputs = [c.toJSON()["output"] for c in layer.get_components()]
    return NumpyEncoder.encodeJSON(outputs)


@app.post("/keview/v1alpha/test/")
async def test_model(test_image: UploadFile = File(...)):
    contents = test_image.file.read()
    image = Image.open(io.BytesIO(contents))
    image = img_to_array(image)
    # TODO: Fix image format
    keras_model.run(image)
    return {"filename": test_image.filename}


def fetch_layer(model: KerasModel, layer_index):
    try:
        return keras_model.get_layers()[int(layer_index)]
    except IndexError:
        logger.error(f"Index out of range: {layer_index}")
        raise HTTPException(status_code=404, detail="Layer not found.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid layer id.")


def fetch_component(layer: Layer, component_index):
    try:
        return layer.get_components()[int(component_index)]
    except IndexError:
        logger.error(f"Index out of range: {component_index}")
        raise HTTPException(status_code=404, detail="Layer not found.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid component id.")
