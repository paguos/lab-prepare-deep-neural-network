from tensorflow import keras
import numpy as np
from keras import backend as K
from abc import ABC, abstractmethod


class Layer(ABC):
    def __init__(self, layer: keras.layers.Layer):
        self.__keras_layer = layer
        self.__input_shape = layer.input_shape
        self.__output_shape = layer.output_shape
        self.__shape = layer.output_shape

    def get_input_shape(self):
        return self.__input_shape

    def get_output_shape(self):
        return self.__output_shape

    def get_keras_layer(self):
        return self.__keras_layer

    #@abstractmethod
    def _set_output(self,output):
        pass


class DenseLayer(Layer):
    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        weights = layer.get_weights()
        weights = np.einsum('kl->lk', weights[0])
        self.__neurons = [Neuron(x, y) for x,y in zip(weights[0], weights[1])]
        self.__activation_function = layer.get_config()["activation"]
        print(self.__activation_function)

    def get_neurons(self):
        return self.__neurons

    def get_activation_function(self):
        return self.__activation_function

    def _set_output(self,layer_output):
       for neuron,neuron_output in zip(self.__neurons,layer_output[0]):
            neuron._set_output(neuron_output);
class ConvolutionLayer(Layer):
    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        weights = layer.get_weights()
        weights[0] = np.einsum('klij->jikl', layer.get_weights()[0])
        self.__featuremaps = [FeatureMap(x, y) for x,y in zip(weights[0], weights[1])]

    def get_featuremaps(self):
        return self.__featuremaps


class FlattenLayer(Layer):
    def __init__(self, layer: keras.layers.Flatten):
        Layer.__init__(self, layer)


class FeatureMap:
    def __init__(self, weights: [], bias: np.float):
        self.__bias = bias
        self.__weights = weights

    def get_weights(self):
        return self.__weights

    def get_bias(self):
        return self.__bias


class Neuron:
    def __init__(self, weights: [], bias: np.float):
        self.__weights = weights
        self.__bias = bias
        self.__output = None
    def get_weights(self):
        return self.__weights

    def get_bias(self):
        return self.__bias
    def _set_output(self,output):
        self.__output=output

    def get_output(self):
        return self.__output


class Model:

    def __init__(self, model: keras.Model):
        self.__model = model
        self.__layers = []
        self.__run_function=K.function([self.__model.input],[layer.output for layer in self.__model.layers])
        for layer in model.layers:
            self.__layers.append(self.__create_layer(layer))

    def get_kera_model(self):
        return self.__model

    def get_layers(self) -> [Layer]:
        return self.__layers

    def run(self,single_element):
        outputs=self.__run_function(np.asarray([single_element]))
        for layer, layer_output in zip(self.__layers,outputs):
            layer._set_output(layer_output)
    def __create_layer(self, layer):
        if isinstance(layer, keras.layers.Dense):
            return DenseLayer(layer)
        if isinstance(layer, keras.layers.Flatten):
            return FlattenLayer(layer)
        if isinstance(layer, keras.layers.Conv2D):
            return ConvolutionLayer(layer)
