from fastapi import FastAPI
from loguru import logger

from tensorflow.python import keras

from keview.models import KerasModel
from keview.utils import NumpyEncoder


logger.info("Loading model ...")
model = keras.models.load_model("examples/test.h5")
keras_model = KerasModel(model)
logger.info("Loading model ... done!")


app = FastAPI()


@app.get("/keview/v1alpha/layers")
async def layers():
    layers = keras_model.get_layers()

    layers_data = []
    index = 0
    for layer in layers:
        layer_data = layer.toJSON()
        layer_data["id"] = index
        layers_data.append(layer_data)
        index = index + 1

    return {"layers": layers_data}


@app.get("/keview/v1alpha/layers/{layer_id}")
async def layer(layer_id):
    layer = keras_model.get_layers()[int(layer_id)]
    layer_data = layer.toJSON()
    layer_data["id"] = layer_id
    return layer_data


@app.get("/keview/v1alpha/layers/{layer_id}/components")
async def components(layer_id):
    layer = keras_model.get_layers()[int(layer_id)]
    components = [c.toJSON() for c in layer.get_components()]
    return NumpyEncoder.encodeJSON(components)


@app.get("/keview/v1alpha/layers/{layer_id}/components/{component_id}")
async def component(layer_id, component_id):
    layer = keras_model.get_layers()[int(layer_id)]
    component = layer.get_components()[int(component_id)]
    return NumpyEncoder.encodeJSON(component.toJSON())


@app.get("/keview/v1alpha/layers/{layer_id}/outputs")
async def outputs(layer_id):
    layer = keras_model.get_layers()[int(layer_id)]
    outputs = [c.toJSON()["output"] for c in layer.get_components()]
    return NumpyEncoder.encodeJSON(outputs)
