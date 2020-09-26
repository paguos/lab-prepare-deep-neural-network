import io
import inflection
import time
import numpy as np

from loguru import logger
from PIL import Image

from fastapi import FastAPI, HTTPException, Request
from fastapi import File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from keras.preprocessing.image import img_to_array
from tensorflow.python import keras

from keview.models import KerasModel
from keview.models import Layer, DenseLayer, FlattenLayer
from keview.utils import MNIST, NumpyEncoder


IMAGES_DIR = "assets/images"


logger.info("Initalizing model ...")
model = keras.models.load_model("assets/mnist_neural_network.h5")
keras_model = KerasModel(model)
input_img = MNIST.get_test_image()
keras_model.run(input_img)


MNIST.save_images(keras_model, input_img)
logger.info("Initalizing model ... done!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/keview/layers_overview")
async def get_all_layers(request: Request):
    return templates.TemplateResponse(
        "layer_overview.html",
        {"request": request}
    )


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
    if isinstance(layer, FlattenLayer):
        outputs = outputs[0]
    return NumpyEncoder.encodeJSON(outputs)


def invert(image):
    return image.point(lambda p: 255 - p)


@app.post("/keview/v1alpha/run/")
async def run_model(test_image: UploadFile = File(...)):
    file_content = test_image.file.read()
    image = Image.open(io.BytesIO(file_content))
    im = image.convert('RGBA')
    r, g, b, a = im.split()
    r, g, b = map(invert, (r, g, b))
    image = Image.merge('RGBA', (r, g, b, a))
    image = image.resize((28, 28)).convert('L')
    image_data = img_to_array(image)/255
    image_data.reshape(28, 28)
    keras_model.run(image_data)
    MNIST.save_images(keras_model, image_data)
    layers = keras_model.get_layers()
    prediction = await outputs(str(len(layers)-1))
    return {
        "prediction": str(np.argmax(prediction))
    }


@app.post("/keview/v1alpha/store-train-image/")
async def saveimg(test_image: UploadFile = File(...)):
    file_content = test_image.file.read()
    image = Image.open(io.BytesIO(file_content))
    im = image.convert('RGBA')
    r, g, b, a = im.split()
    r, g, b = map(invert, (r, g, b))
    image = Image.merge('RGBA', (r, g, b, a))
    image = image.resize((28, 28)).convert('L')

    image.save("train-data/"+time.strftime("%Y%m%d-%H%M%S") +
               "_"+test_image.filename)
    return {
        "details": f"Successfully: {test_image.filename}"
    }


@app.get("/")
async def home(request: Request):
    template_data = {
        "request": request
    }
    return templates.TemplateResponse("index.html", template_data)


@app.get("/keview/layers/{layer_id}")
async def display_layer(request: Request, layer_id: str):

    layer = fetch_layer(keras_model, layer_id)
    layer_name = inflection.underscore(type(layer).__name__)

    componentsvar = layer.get_components()
    template_data = {
        "layer_id": layer_id,
        "max_layer_id": len(keras_model.get_layers())-1,
        "request": request,
    }
    if isinstance(layer, DenseLayer):

        template_data["component"] = {

            "name": type(componentsvar[0]).__name__,
            "count": len(componentsvar),
            "neuronalInput": await outputs(str(int(layer_id)-1)),
            "neuronalWeights": await components(layer_id),
        }
    elif isinstance(layer, FlattenLayer):
        pass
    else:
        images = MNIST.list_images(int(layer_id))
        images_before = MNIST.list_images(int(layer_id)-1)
        images.sort()
        images_before.sort()
        template_data["images"] = images
        template_data["imagesBefore"] = images_before
        template_data["component"] = {
            "name": type(componentsvar[0]).__name__,
            "count": len(componentsvar),
            "neuronalWeights": await components(layer_id),
        }
    return templates.TemplateResponse(
        f"{layer_name}.html",
        template_data
    )


@app.get("/keview/run")
async def run_draw(request: Request):
    return templates.TemplateResponse(
        "run_draw.html",
        {"request": request}
    )


@app.get("/keview/train")
async def train_draw(request: Request):
    return templates.TemplateResponse(
        "train_draw.html",
        {"request": request}
    )


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
