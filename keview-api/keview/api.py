import io
import inflection

from fastapi import FastAPI, HTTPException, Request
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from keras.preprocessing.image import img_to_array
from loguru import logger
from PIL import Image
from tensorflow.python import keras

from keview.models import KerasModel
from keview.models import Layer, DenseLayer, FlattenLayer
from keview.utils import MNIST, NumpyEncoder

IMAGES_DIR = "assets/images"


logger.info("Initalizing model ...")
model = keras.models.load_model("assets/keview_model.h5")
keras_model = KerasModel(model)
keras_model.run(MNIST.get_test_image())
MNIST.save_images(keras_model)
logger.info("Initalizing model ... done!")

app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="assets/templates")


@app.get("/keview/v1alpha/layers")
async def layers():
    layers = keras_model.get_layers()

    layers_data = []
    for i in range(0, len(layers)):
        layer_data = layers[i].toJSON()
        layer_data["id"] = i
        layers_data.append(layer_data)

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


@app.get("/")
async def display_layer(request: Request):
    template_data = {
        "request": request
    }
    return templates.TemplateResponse("index.html", template_data)



@app.get("/keview/v1alpha/layers/{layer_id}/display")
async def display_layer(request: Request, layer_id: str):
    layer = fetch_layer(keras_model, layer_id)
    layer_name = inflection.underscore(type(layer).__name__)
    components = layer.get_components()

    template_data = {
        "layer_id": layer_id,
        "request": request,
    }

    if isinstance(layer, DenseLayer):
        template_data["component"] = {
            "name": type(components[0]).__name__,
            "count": len(components)
        }
    elif isinstance(layer, FlattenLayer):
        pass
    else:
        images = MNIST.list_images(int(layer_id))
        template_data["images"] = images
        template_data["component"] = {
            "name": type(components[0]).__name__,
            "count": len(components)
        }

    return templates.TemplateResponse(
        f"{layer_name}.html",
        template_data
    )


@app.post("/keview/v1alpha/test/")
async def run_model(test_image: UploadFile = File(...)):
    file_content = test_image.file.read()
    image = Image.open(io.BytesIO(file_content)).resize((28, 28)).convert("1")
    image_data = img_to_array(image)
    image_data.reshape(28, 28)
    keras_model.run(image_data)
    return {
        "details": f"Successfully tested image: {test_image.filename}"
    }


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
        raise HTTPException(status_code=404, detail="Component not found.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid component id.")
