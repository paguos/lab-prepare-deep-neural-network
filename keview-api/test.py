from tensorflow.python import keras
import keview
import numpy as np
import matplotlib.pyplot as plt
from keras import backend as K
model=keras.models.load_model("test.h5")
data = keras.datasets.mnist
(train_images_temp, train_labels), (test_images_temp, test_labels) = data.load_data()
train_images = train_images_temp / 255.0
print(np.shape(train_images))
test_images = test_images_temp / 255.0
train_images = train_images.reshape(60000,28,28,1)
test_images = test_images.reshape(10000,28,28,1)
image=23

print(model.summary())
t = keview.Model(model)
element=np.zeros((28,28,3),np.float32)
plt.imshow(test_images_temp[image],cmap='binary')
t.run(test_images[image])
plt.show()
plt.imshow(t.get_layers()[3].get_featuremaps()[-1].get_output(),cmap="binary")
l=t.get_layers()[-1].get_neurons();
for i in range(len(l)):
    print(i,": ",l[i].get_output())
plt.show()
