#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 21:46:12 2019

@author: chinshu
"""
#######


import cv2
import glob
import numpy as np
import os.path as path
from scipy import misc
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Activation,Dense, Conv2D, MaxPooling2D,Input, Convolution2D, Flatten
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import math
import os 
from keras.optimizers import Adam
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn import metrics
import pandas as pd
import seaborn as sns
from skimage import color
from skimage import io
from sklearn.decomposition import NMF
from sklearn import metrics



# =============================================================================
# reading the images from the specified path
# =============================================================================
path_of_image = 'D:/Study/Masters/Thesis/dataset/NEU-DET/NEU-DET/IMAGES'
file_paths = glob.glob(path.join(path_of_image, '*.jpg'))
len(file_paths)
file_paths[:10]
# Loading the images and resizing it to 40,40
images = [cv2.imread(fpath) for fpath in file_paths]
images=[cv2.resize(image,(40,40)) for image in images ]
images = np.asarray(images)

# Getting image size
image_size = np.asarray([images.shape[1], images.shape[2], images.shape[3]])
print(image_size)
# =============================================================================
# scalling and applying gausian blur
# =============================================================================
#scalling
scaling = images / 255
#applying gaussian blur
import os
import matplotlib.pyplot as plt
write_path = 'D:/study/New'
os.chdir(write_path)
no_noise = []
for i in range(len(scaling)):
    blur = cv2.GaussianBlur(scaling[i], (5, 5), 0)   # change the kernal size to 3x3 for generating blur images 
    no_noise.append(blur)
    # storing the images into a folder
    img = no_noise[i]
    plt.imshow(img)
    plt.savefig("{}".format(os.path.split(file_paths[i])[-1]))
    
##################Reading the gaussian blur images#############################

path_of_image2 = 'D:/study/gaussianblur'    # path of gaussian blur for separate 3x3 and 5x5 kernal size
file_paths2 = glob.glob(path.join(path_of_image2, '*.jpg'))


# loading the images
img = [color.rgb2gray(io.imread(file_path,0)) for file_path in file_paths2]
img1 = np.asarray(img)
len(img1)


# applying Non-negative matrix factorization
list_img = []
for i in range(img1.shape[0]):
    model = NMF(n_components=20, init='random', random_state=0)
    W = model.fit_transform(img1[i])
    H = model.components_
    matrix = np.dot(W,H)
    list_img.append(matrix)


# reading labels
images_nmf = np.asarray(list_img)
images_nmf.shape
n_images = images_nmf.shape[0]

class_names =['crazing','inclusion','patches','pitted_surface','rolled-in_scale','scratches']
y = []
for i in range(n_images):
    filename = os.path.basename(file_paths2[i])
    for j in class_names:
        if j in filename:
            idx = class_names.index(j)
            y.append(int(idx))


# will give six image classes
no_of_classes = np.unique(y).shape[0]

# encoding categorical data
Y = np_utils.to_categorical(y, no_of_classes)

#resizing image 
images_nmf.resize(1800,200,200,1)
X = images_nmf
# normalizing data to bring in range of 0 to 1
s =  images_nmf/np.max(images_nmf)        
X = s

#dividing the data into training set and test set
x_train, x_test, y_train, y_test = train_test_split(X , Y, test_size = 0.20, random_state = 0)
###############################################################################



# Initilizaing Convolutional Neural Network
model_classifier = Sequential()

# convolution layer with pooling
model_classifier.add(Convolution2D(32,3,3, input_shape = (200,200,1), activation='relu'))
model_classifier.add(Convolution2D(32,3,3, activation='relu'))
model_classifier.add(MaxPooling2D(pool_size=(2,2)))
# convolution layer with pooling 
model_classifier.add(Convolution2D(64,3,3, activation='relu'))
model_classifier.add(Convolution2D(64,3,3, activation='relu'))
model_classifier.add(MaxPooling2D(pool_size=(2,2)))
# convolution layer with pooling
model_classifier.add(Convolution2D(128,3,3, activation='relu'))
model_classifier.add(Convolution2D(128,3,3, activation='relu'))
model_classifier.add(MaxPooling2D(pool_size=(2,2)))
#step3 flattening
model_classifier.add(Flatten())
#step4 full connected layer
model_classifier.add(Dense(output_dim = 256, activation='relu'))
model_classifier.add(Dense(output_dim = 6, activation = 'softmax'))
model_classifier.compile(Adam(lr = 0.0001),loss = 'categorical_crossentropy',metrics = ['accuracy'])

# training the model using training set data
model_classifier.fit(x_train,y_train,
               epochs=20,
               validation_data=(x_test,y_test)) 

# evaluating the model based on testing data
score = model_classifier.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])    
print('Test accuracy:', score[1])    

#ploting confusion matrix

y_pred = model_classifier.predict(x_test)
Y_pred = np.argmax(y_pred, 1) # Decode Predicted labels
Y_test = np.argmax(y_test, 1) # Decode labels

confusion_matrix = confusion_matrix(Y_test,Y_pred)

confusion_matrix_df = pd.DataFrame(confusion_matrix,
                     index = class_names, 
                     columns = class_names)

plt.figure(figsize=(6,4))
sns.heatmap(confusion_matrix_df, annot= True)
plt.title('CNN \nAccuracy:{0:.3f}\n'.format(accuracy_score(Y_test, Y_pred)))
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show() 



#will give the precision and recall for all the classes
print(metrics.classification_report(Y_test,Y_pred,digits=3))



















