from PIL import Image
import io

from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile
from keras.preprocessing.image import img_to_array
from loguru import logger
from tensorflow.python import keras

from keview.models import KerasModel, Layer
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
        index += 1

    return {"layers": layers_data}


@app.get("/keview/v1alpha/layers/{layer_id}")
async def layer(layer_id):
    layer = fetch_layer(keras_model, layer_id)
    layer_data = layer.toJSON()
    layer_data["id"] = layer_id
    return layer_data


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
