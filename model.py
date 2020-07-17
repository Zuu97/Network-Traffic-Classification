import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
# from tensorflow import keras
from tensorflow.keras.layers import Dense, Input, Dropout, Embedding, LSTM, BatchNormalization
from tensorflow.keras.models import model_from_json, load_model
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

import tensorflow.keras.backend as K
import logging
logging.getLogger('tensorflow').disabled = True

from variables import*
from util import load_data
import argparse
import operator
from collections import Counter

'''  Use following command to run the script

                python model.py --data_set=Train

'''

class NetworkTrafficClassifier(object):
    def __init__(self, Train):
        self.Train = Train
        encoder, Inputs, labels = load_data(Train)
        self.X = Inputs
        self.Y = labels
        self.encoder = encoder
        if Train:
            self.num_classes = int(labels.shape[1])
        print("Input Shape : {}".format(self.X.shape))
        print("Label Shape : {}".format(self.Y.shape))

    def classifier(self):
        inputs = Input(shape=(n_features,))
        x = Dense(dense1, activation='tanh')(inputs)
        # x = BatchNormalization()(x)
        x = Dense(dense2, activation='tanh')(x)
        x = Dense(dense2, activation='tanh')(x)
        x = Dense(dense3, activation='tanh')(x)
        x = Dense(dense3, activation='tanh')(x)
        x = Dense(dense3, activation='tanh')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        self.model = Model(inputs, outputs)

    @staticmethod
    def acc(y_true,y_pred):
        targ = K.argmax(y_true, axis=-1)
        pred = K.argmax(y_pred, axis=-1)
        correct = K.cast(K.equal(targ, pred), dtype='float32')

        Pmax = K.cast(K.max(y_pred, axis=-1), dtype='float32')
        Pmax = Pmax * correct
        mask = K.cast(K.greater(Pmax, custom_acc), dtype='float32')

        return K.mean(mask)


    def train(self):
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=Adam(learning_rate),
            # metrics=['accuracy'],
            metrics=[NetworkTrafficClassifier.acc]
        )
        self.history = self.model.fit(
                            self.X,
                            self.Y,
                            batch_size=batch_size,
                            epochs=num_epoches,
                            validation_split=validation_split
                            )

    def plot_metrics(self):
        loss_train = self.history.history['loss']
        loss_val = self.history.history['val_loss']
        plt.plot(np.arange(1,num_epoches+1), loss_train, 'r', label='Training loss')
        plt.plot(np.arange(1,num_epoches+1), loss_val, 'b', label='validation loss')
        plt.title('Training and Validation loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.savefig(loss_img)
        plt.legend()
        plt.show()

        acc_train = self.history.history['acc']
        acc_val = self.history.history['val_acc']
        plt.plot(np.arange(1,num_epoches+1), acc_train, 'r', label='Training Accuracy')
        plt.plot(np.arange(1,num_epoches+1), acc_val, 'b', label='validation Accuracy')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.savefig(acc_img)
        plt.legend()
        plt.show()

    def load_model(self, model_weights):
        loaded_model = load_model(model_weights)
        loaded_model.compile(
                        loss='categorical_crossentropy',
                        optimizer=Adam(learning_rate),
                        # metrics=['accuracy'],
                        metrics=[NetworkTrafficClassifier.acc]
                        )
        self.model = loaded_model

    def save_model(self ,model_weights):
        self.model.save(model_weights)

    def evaluation(self):
        Ypred = self.model.predict(self.X)
        Ppred = np.max(Ypred, axis=-1)
        unk = (Ppred <= custom_acc)
        Punk = np.mean(unk) * 100
        print("Unknown {} data Percentage : {}%".format(
                                        "Train" if self.Train else "Test",
                                        round(Punk,3))
                                        )

    def predict_classes(self):
        Ypred = self.model.predict(self.X)

        N = Ypred.shape[0]
        Ppred = np.argmax(Ypred, axis=-1)
        Ponehot = np.zeros((N, train_classes), dtype=np.int64)
        for i in range(N):
           j = Ppred[i]
           Ponehot[i,j] = 1
        Pclasses = self.encoder.inverse_transform(Ponehot).reshape(-1,)
        class_count = dict(Counter(Pclasses.tolist()))
        class_count = sorted(class_count.items(),key=operator.itemgetter(1),reverse=True)
        for label, value in class_count:
            fraction = (value/N)*100
            fraction = round(fraction, 3)
            print("{} : {}%".format(label,fraction))

    def predicts(self,X):
        return self.model.predict(X)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    my_parser = argparse.ArgumentParser(description='Model parameters and hyperparameters')

    my_parser.add_argument('--data_set',
                        metavar='train or test',
                        type=str,
                        help='predictions based on required dataset after training the model')

    args = my_parser.parse_args()

    Train = True if args.data_set.lower() == 'train' else False

    model = NetworkTrafficClassifier(Train)
    if os.path.exists(model_weights):
        print("Loading the model !!!")
        model.load_model(model_weights)
    else:
        print("Training the model !!!")
        model.classifier()
        model.train()
        model.plot_metrics()
        model.save_model(model_weights)
    model.evaluation()
    # model.predict_classes()