import keras
import keview
test = keras.Sequential()
test.add(keras.layers.Conv2D(filters=8, kernel_size=(5, 5), input_shape=(28, 28, 3)))
test.add(keras.layers.Flatten())
test.add(keras.layers.Dense(5,activation="sigmoid"))
test.add(keras.layers.Dense(6,activation="sigmoid"))

print(test.summary())


t = keview.Model(test)



for i in range(len(t.get_layers())):
    print("layer ", i, " input shape: ", t.get_layers()[i].get_input_shape())
    print("layer ", i, " output shape: ", t.get_layers()[i].get_output_shape())
    print("")
    if(isinstance(t.get_layers()[i],keview.DenseLayer)):
        f=keras.activations.get(t.get_layers()[i].get_activation_function())
        print(f(0.5))
