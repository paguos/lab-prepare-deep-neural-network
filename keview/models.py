import numpy as np

from abc import ABC, abstractmethod
from tensorflow.python import keras


class Layer(ABC):
    def __init__(self, layer: keras.layers.Layer):
        self.__keras_layer = layer
        self.__input_shape = layer.input_shape
        self.__output_shape = layer.output_shape
        self.__shape = layer.output_shape

    @property
    def name(self):
        return self.__class__.__name__

    def get_input_shape(self):
        return self.__input_shape

    def get_output_shape(self):
        return self.__output_shape

    def get_keras_layer(self):
        return self.__keras_layer

    @abstractmethod
    def _set_output(self, output):
        pass

    @abstractmethod
    def get_components():
        pass

    def toJSON(self):
        return {
            "name":  self.name,
            "input_shape":  self.__input_shape,
            "output_shape": self.__output_shape,
        }


class DenseLayer(Layer):
    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        weights = layer.get_weights()
        weights[0] = np.einsum('kl->lk', weights[0])
        self.__neurons = [self.Neuron(x, y)
                          for x, y in zip(weights[0], weights[1])]
        self.__activation_function = layer.get_config()["activation"]

    def get_neurons(self):
        return self.__neurons

    def get_activation_function(self):
        return self.__activation_function

    def get_components(self):
        return self.__neurons

    def _set_output(self, layer_output):
        for neuron, neuron_output in zip(self.__neurons, layer_output[0]):
            neuron._set_output(neuron_output)

    class Neuron:
        def __init__(self, weights: [], bias: np.float):
            self.__weights = weights
            self.__bias = bias
            self.__output = None

        def get_weights(self):
            return self.__weights

        def get_bias(self):
            return self.__bias

        def _set_output(self, output):
            self.__output = output

        def get_output(self):
            return self.__output

        def toJSON(self):
            return {
                "weights": self.__weights,
                "bias": self.__bias,
                "output": self.__output,
            }


class ConvolutionLayer(Layer):

    def __init__(self, layer: keras.layers.Dense):
        Layer.__init__(self, layer)

        weights = layer.get_weights()
        weights[0] = np.einsum('klij->jikl', layer.get_weights()[0])
        self.__featuremaps = [self.FeatureMap(
            x, y) for x, y in zip(weights[0], weights[1])]

    def get_featuremaps(self):
        return self.__featuremaps

    def get_components(self):
        return self.__featuremaps

    def _set_output(self, layer_output):
        layer_output = np.einsum(
            'abc->cab', np.reshape(layer_output, np.shape(layer_output)[1:]))
        for featuremap, featuremap_output in zip(
                self.__featuremaps, layer_output):
            # print(np.shape(featuremap_output))
            featuremap._set_output(featuremap_output)

    class FeatureMap:
        def __init__(self, weights: [], bias: np.float):
            self.__bias = bias
            self.__weights = weights
            self.__output = None

        def get_weights(self):
            return self.__weights

        def get_bias(self):
            return self.__bias

        def _set_output(self, output):
            self.__output = output

        def get_output(self):
            return self.__output

        def toJSON(self):
            return {
                "weights": self.__weights,
                "bias": self.__bias,
                "output": self.__output,
            }


class FlattenLayer(Layer):
    def __init__(self, layer: keras.layers.Flatten):
        Layer.__init__(self, layer)
        self.__helpers = [self.Helper()]

    def _set_output(self, output):
        self.__helpers[0]._set_output(output[0])

    def get_components(self):
        return self.__helpers  # def toJSON(self):

    class Helper:
        def __init__(self):
            self.__output = []
            pass

        def _set_output(self, output):
            self.__output = output

        def toJSON(self):
            return {
                "output": self.__output
            }


class BatchNormalizationLayer(Layer):

    def __init__(self, layer: keras.layers.BatchNormalization):
        Layer.__init__(self, layer)
        weights = np.einsum('ab->ba', layer.get_weights())
        self.__normalization_diminsions = [
            self.NormalizationDimension(w) for w in weights]

    def get_normalization_dimensions(self):
        return self.__normalization_diminsions

    def get_components(self):
        return self.__normalization_diminsions

    def _set_output(self, output):
        output = np.einsum(
            'abc->cab', np.reshape(output, np.shape(output)[1:]))
        for dimension, dimension_output in zip(
                self.__normalization_diminsions, output):
            dimension._set_output(dimension_output)

    class NormalizationDimension:
        def __init__(self, weights):
            self.__gamma = weights[0]
            self.__beta = weights[1]
            self.__mean = weights[2]
            self.__variance = weights[3]
            self.__output = None

        def get_gamma(self):
            return self.__gamma

        def get_beta(self):
            return self.__beta

        def get_mean(self):
            return self.__mean

        def get_variance(self):
            return self.__variance

        def _set_output(self, output):
            self.__output = output

        def get_output(self):
            return self.__output

        def toJSON(self):
            return {
                "gamma": self.__gamma,
                "beta": self.__beta,
                "mean": self.__mean,
                "variance": self.__variance,
                "output": self.__output,
            }


class MaxPoolingLayer(Layer):

    def __init__(self, layer: keras.layers.BatchNormalization):
        Layer.__init__(self, layer)
        self._max_pooling_dimensions = [
            self.MaxPoolingDimension() for i in range(layer.input_shape[-1])]

    def get_max_pooling_dimensions(self):
        return self._max_pooling_dimensions

    def get_components(self):
        return self._max_pooling_dimensions

    def _set_output(self, output):
        output = np.einsum(
            'abc->cab', np.reshape(output, np.shape(output)[1:]))
        for dimension, dimension_output in zip(
                self._max_pooling_dimensions, output):
            dimension._set_output(dimension_output)

    class MaxPoolingDimension:
        def __init__(self):
            self.__output = None

        def _set_output(self, output):
            self.__output = output

        def get_output(self):
            return self.__output

        def toJSON(self):
            return {
                "output": self.__output,
            }


class KerasModel:

    def __init__(self, model: keras.Model):
        self.__model = model
        self.__layers = []
        self.__run_function = keras.backend.function(
            [self.__model.input],
            [layer.output for layer in self.__model.layers]
        )
        for layer in model.layers:
            self.__layers.append(self.__create_layer(layer))

    def get_kera_model(self):
        return self.__model

    def get_layers(self) -> [Layer]:
        return self.__layers

    def run(self, single_element):
        outputs = self.__run_function(np.asarray([single_element]))
        for layer, layer_output in zip(self.__layers, outputs):
            layer._set_output(layer_output)

    def __create_layer(self, layer):
        if isinstance(layer, keras.layers.Dense):
            return DenseLayer(layer)
        if isinstance(layer, keras.layers.Flatten):
            return FlattenLayer(layer)
        if isinstance(layer, keras.layers.Conv2D):
            return ConvolutionLayer(layer)
        if isinstance(layer, keras.layers.Flatten):
            return FlattenLayer(layer)
        if isinstance(layer, (
            keras.layers.BatchNormalization,
            keras.layers.normalization_v2.BatchNormalization
        )):
            return BatchNormalizationLayer(layer)
        if isinstance(layer, keras.layers.MaxPooling2D):
            return MaxPoolingLayer(layer)
        else:
            return None
