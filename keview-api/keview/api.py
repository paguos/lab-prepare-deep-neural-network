from PIL import Image
import io

from nnv import NNV
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException, Request
from fastapi import File, UploadFile
from keras.preprocessing.image import img_to_array
from loguru import logger
from tensorflow.python import keras

from keview.models import KerasModel, Layer
from keview.utils import NumpyEncoder

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



logger.info("Loading model ...")
model = keras.models.load_model("examples/test.h5")
keras_model = KerasModel(model)
logger.info("Loading model ... done!")


app = FastAPI()

# https://fastapi.tiangolo.com/advanced/templates/
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/visualization/summary")
async def visualization():
    # show the summary of model
    return model.summary()


@app.get("/visualization/test")
async def print_filter():
    layer_list = []
    layers_info = {}
    for i in model.layers:
        #print("name: " + str(layers_info[i.name]))
        layers_info[i.name] = i.get_config()

    layers = keras_model.get_layers()
    layer_dense = [7, 8]  # [1, 4, 7, 11, 15]
    layer_conv = [0, 3]
    layer_batch = [1, 4]
    layer_max_pooling = [2, 5]
    layer_flatten = 6
    # plot the filters
    # fig, ax = plt.subplots(nrows=1, ncols=5)
    for i in range(2):
        # print('weights: ' + str(layers[7].get_neurons()[0].get_weights()[0]))
        current_layer = layers[layer_dense[i]].get_neurons()
    #for i in range(2):
    #    print(str(layers[layer_max_pooling].get_max_pooling_dimensions()[0]))
    '''
    layersList = [
        {"title": "conv2d", "units": 8, "color": "darkBlue"},
        {"title": "batch_normalization", "units": 8},
        {"title": "max_pooling2d", "units": 8},
        {"title": "conv2d_1", "units": 16},
        {"title": "batch_normalization_1", "units": 16},
        {"title": "max_pooling2d_1", "units": 16},
        {"title": "flatten", "units": 400},
        {"title": "dense", "units": 100},
        {"title": "dense_1", "units": 10, "color": "darkBlue"},
    ]
    '''
    layersList = [
        {"title": "conv2d", "units": 8, "color": "darkBlue"},
        {"title": "batch_normalization", "units": 8},
        {"title": "max_pooling2d", "units": 8},
    ]
    NNV(layersList).render(save_to_file="my_example.png")




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
        bias = featuremap.get_bias()
        weights = featuremap.get_weights()

        print(f"bias: {bias}")
        print(f"weights: {weights}")

        return templates.TemplateResponse("conv2d_layer.html", {"request": request, "bias": bias, "weights": weights, "output": output})

    # case batch_normalization_layer
    elif layer_id == "1" or layer_id == "4":
        batch_normalization_layer = keras_model.get_layers()[int(layer_id)].get_normalization_dimensions()
        for i in range(len(batch_normalization_layer)):
            # TODO: Debug this
            output = batch_normalization_layer[i].get_output()
            print(f"output: {output}")
            #plt.imshow(output, cmap="binary")
            #plt.show()

            beta = batch_normalization_layer[i].get_beta()
            gamma = batch_normalization_layer[i].get_gamma()
            mean = batch_normalization_layer[i].get_mean()
            variance = batch_normalization_layer[i].get_variance()


            # TODO: Write this to list and hand to FE
            print(f"beta: {beta}, mean: {mean}, gamma: {gamma}, mean: {mean}, variance: {variance}")

        return templates.TemplateResponse("batch_normalization_layer.html", {"request": request})

    # case max_pooling2d layer
    elif layer_id == "2" or layer_id == "5":
        # TODO: show max_poolingdimension + output (NO PARAMS)
        max_pooling_dim = keras_model.get_layers()[int(layer_id)].get_max_pooling_dimensions()
        for i in range(len(max_pooling_dim)):
            print(max_pooling_dim[i].get_output())
            #plt.imshow(max_pooling_dim[i].get_output())
            #plt.show()

        return templates.TemplateResponse("max_pooling_layer.html", {"request": request})

    # flatten layer
    elif layer_id == "6":
        # TODO: skip (maybe find some useful text about flatten layer)
        return templates.TemplateResponse("flatten_layer.html", {"request": request})

    # dense layer
    elif layer_id == "7" or layer_id == "8":
        neurons = keras_model.get_layers()[int(layer_id)].get_neurons()

        # TODO: Write all neurons into a list (neuron, weights-array, bias)
        print(f"Neurons: {neurons[0].get_weights()}")
        return templates.TemplateResponse("dense_layer.html", {"request": request})

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
