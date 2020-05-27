import keras
import numpy as np


class Layer:
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


class DenseLayer(Layer):
    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        we = layer.get_weights()
        we[0] = np.einsum('kl->lk', we[0])
        self.__neurons = [Neuron(we[0][i], we[1][i]) for i in range(len(we[0]))]

    def get_neutons(self):
        return self.__neurons


class ConvolutionLayer(Layer):
    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        we = layer.get_weights()
        we[0] = np.einsum('klij->jikl', layer.get_weights()[0])
        self.__featuremaps = [FeatureMap(we[0][i], we[1][i]) for i in range(len(we[0]))]

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
    def __init__(self, weights: [], input_bias: np.float):
        self.__weights = weights
        self.__bias = input_bias

    def get_weights(self):
        return self.__weights

    def get_bias(self):
        return self.__bias


class Model:

    def __init__(self, model: keras.Model):
        self.__model = model
        self.__layers = []
        for layer in model.layers:
            self.__layers.append(self.__create_layer(layer))

    def get_layers(self) -> [Layer]:
        return self.__layers

    def __create_layer(self, layer):
        if isinstance(layer, keras.layers.Dense):
            return DenseLayer(layer)
        if isinstance(layer, keras.layers.Flatten):
            return FlattenLayer(layer)
        if isinstance(layer, keras.layers.Conv2D):
            return ConvolutionLayer(layer)
