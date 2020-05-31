from tensorflow import keras
import keview
import numpy as np
from keras import backend as K
test = keras.Sequential()
test.add(keras.layers.Conv2D(filters=8, kernel_size=(5, 5), input_shape=(28, 28, 3)))
test.add(keras.layers.Flatten())
test.add(keras.layers.Dense(5,activation="sigmoid"))
test.add(keras.layers.Dense(6,activation="sigmoid"))

print(test.summary())


t = keview.Model(test)
element=np.zeros((28,28,3),np.float32)
print(test(np.asarray([element])))
get_output = K.function([test.layers[0].input],
                        [test.layers[0].output])
[conv_outputs] = get_output(np.asarray([element]))
print(id(test))
t.run(element)
for i in range(len(t.get_layers())):
    print("layer ", i, " input shape: ", t.get_layers()[i].get_input_shape())
    print("layer ", i, " output shape: ", t.get_layers()[i].get_output_shape())
    print("")
    if(isinstance(t.get_layers()[i],keview.DenseLayer)):
        print(t.get_layers()[i].get_neurons()[0].get_output())