'''
Main file for cough detection and classification functionality
Together with this file, we provide two trained models (./models/esc50_model and ./models/cv_model) that will be used
for predictions. As long as the models exist in the same folder as this file, things will work.
However, if at any point, for any reason, the models are non-existent, follow the steps below.

If there are no trained models, the script will make new models to train.
To do this, the script will look for MFCC files within the directory (./mfcc_esc50 and ./mfcc_coughvid).
If these files do not exist, then the script will extract MFCC from the datasets.

As we do not provide the datasets themselves in this repo, the user will have to download them and place them in the directory.
Here are the steps to setup the datasets:

1) ESC50 dataset
Download ESC50 dataset: https://github.com/karolpiczak/ESC-50
Copy the audio folder from the repo and place it into this file's directory.
Rename the folder into "audio_esc50"

2) Coughvid dataset
Download Coughvid dataset: https://zenodo.org/record/4498364
Extract public_dataset folder from the zip file and place it into this file's directory.
Make sure FFMPEG is installed in your system
Run converter.py (make sure to have 20GB worth of space before doing this... this dataset is huge...)
'''

import os
# ignore INFO and WARNING
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# import sys
# import pathlib 

# Comet_ML experiment
from comet_ml import Experiment
# from keras.engine import sequential
# from keras.metrics import accuracy

import numpy as np
import pandas as pd
import librosa

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
# from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
# import tensorflow as tf
from tensorflow import keras



def main(input, parent):
    
    experiment = Experiment(
        api_key="pBIdcBtHz1ROYgtkqG0f3B4fD",
        project_name="ai4covid19",
        workspace="meoridlans97",
    )

    print(f'Input file received: {input}')

    # path to this file's directory
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # create AI class
    ai4c19 = AI4Covid19()

    # try and find model on local
    # if models not found, train new models and save them to directory
    models_path = f'{dir_path}/models'
    if os.path.isdir(models_path):
        ai4c19.load_esc(models_path)
        ai4c19.load_cv(models_path)
    else:
        features_df = extractMFCC_esc(dir_path)
        ai4c19.train_esc(features_df)
        ai4c19.save_esc(models_path)
        features_cv_df = extractMFCC_cv(dir_path)
        ai4c19.train_cv(features_cv_df)
        ai4c19.save_cv(models_path)

    return ai4c19.predict_cough(input, parent)

# helper method
# extracts mfcc from file
# returns mfcc
def generateMFCC(file):
    audio, sr = librosa.load(file, res_type='kaiser_fast', duration=5.0)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    mfcc_processed = np.mean(mfcc.T, axis=0)
    return mfcc_processed

# this method goes through the ESC50 folder, and extracts mfcc from every audio files
def extractMFCC_esc(dir_path):
    df_esc = pd.read_csv(f'{dir_path}/dataset_metas/esc50.csv')

    # extracting features from esc50 audio files
    features = []
    df_esc_fc = df_esc[['filename', 'category']].copy()
    mfcc_esc50_path = f'{dir_path}/mfcc_esc50'
    # if theres no mfcc for esc50 dataset,
    # extract mfcc from every file in esc50 dataset
    if not os.path.isdir(mfcc_esc50_path):
        # creating new dir
        print('MFCC folder for ESC50 dataset not found. Creating new directory.')
        os.mkdir(mfcc_esc50_path)

        # checking if audio folder does not exists
        audio_path = f'{dir_path}/audio_esc50'
        if not os.path.isdir(audio_path):
            raise Exception('ESC50 folder not found.')

        # extract MFCC for all audio files
        print('Extracting MFCC for ESC50...')
        for row in df_esc_fc.itertuples(index=False):
            # check if file does not exist
            if not os.path.isfile(f'{audio_path}/{row[0]}'):
                str = f'Audio file {row[0]} not found.'
                raise Exception(str)

            # extract MFCC
            data = generateMFCC(f'{audio_path}/{row[0]}')
            features.append([data, row[1]])
            np.savetxt(f'{mfcc_esc50_path}/{row[0][:-4]}_mfcc.txt', data)
            print(f'Finished creating MFCC for {row[0]}')
            
    else:
        print('MFCC folder for ESC50 found. Loading MFCC files...')
        for row in df_esc_fc.itertuples(index=False):
            mfcc_file = f'{mfcc_esc50_path}/{row[0][:-4]}_mfcc.txt'

            # check if file does not exist
            if not os.path.isfile(mfcc_file):
                str = f'MFCC for {row[0]} not found'
                raise Exception(str)

            # load MFCC from file
            data = np.loadtxt(mfcc_file)
            features.append([data, row[1]])
            print(f'Finished loading MFCC for {row[0]}')

    # convert features into dataframe
    features_df = pd.DataFrame(features, columns=['feature','label'])
    return features_df

# this method goes through the Coughvid folder, and extracts mfcc from every audio files
def extractMFCC_cv(dir_path):
    # read metadata for coughvid
    df_cv = pd.read_csv(f'{dir_path}/dataset_metas/metadata_compiled.csv')
    # remove rows with null status
    df_cv = df_cv.loc[df_cv['status'].notnull()]
    # remove rows with cough probability less than 0.6
    df_cv = df_cv.loc[df_cv['cough_detected'] >= 0.6]

    # extract features from coughvid audio files
    features_cv = []
    df_cv_us = df_cv[['uuid', 'status']].copy()
    mfcc_cv_path = f'{dir_path}/mfcc_coughvid'

    if not os.path.isdir(mfcc_cv_path):
        # create new directory
        print('MFCC folder for Coughvid dataset not found. Creating new directory.')
        os.mkdir(mfcc_cv_path)

        # checking if audio folder does not exists
        audio_path = f'{dir_path}/audio_coughvid'
        if not os.path.isdir(audio_path):
            raise Exception('Coughvid folder not found.')

        # extract MFCC for all audio files
        print('Extracting MFCC for Coughvid...')
        for row in df_cv_us.itertuples(index=False):
            # check if file does not exist
            if not os.path.isfile(f'{audio_path}/{row[0]}.wav'):
                str = f'Audio file {row[0]} not found.'
                raise Exception(str)

            # extract MFCC
            data = generateMFCC(f'{audio_path}/{row[0]}.wav')
            features_cv.append([data, row[1]])
            np.savetxt(f'{mfcc_cv_path}/{row[0]}_mfcc.txt', data)
            print(f'Finished creating MFCC for {row[0]}.wav')
    else:
        print('MFCC folder for Coughvid found. Loading MFCC files...')
        for row in df_cv_us.itertuples(index=False):
            mfcc_file = f'{mfcc_cv_path}/{row[0]}_mfcc.txt'

            # check if file does not exist
            if not os.path.isfile(mfcc_file):
                str = f'MFCC for {row[0]}.wav not found'
                raise Exception(str)

            # load MFCC from file
            data = np.loadtxt(mfcc_file)
            features_cv.append([data, row[1]])
            print(f'Finished loading MFCC for {row[0]}.wav')

    # convert features into dataframe
    features_cv_df = pd.DataFrame(features_cv, columns=['feature','label'])
    return features_cv_df

class AI4Covid19():

    def __init__(self):
        self.le_esc = LabelEncoder()
        self.le_cv = LabelEncoder()
        self.model_esc = Sequential()
        self.model_cv = Sequential()

    # trains a model for the ESC50 dataset
    def train_esc(self, df_esc_feat):
        X_esc = np.array(df_esc_feat.feature.tolist())
        y_esc = np.array(df_esc_feat.label.tolist())

        yy_esc = to_categorical(self.le_esc.fit_transform(y_esc))

        # split dataset
        X_esc_train, X_esc_test, y_esc_train, y_esc_test = train_test_split(X_esc, yy_esc, test_size=0.2, random_state=10)

        num_labels = yy_esc.shape[1]
        # filter_size = 2

        # building neural network
        self.model_esc.add(Dense(256))
        self.model_esc.add(Activation('relu'))
        self.model_esc.add(Dropout(0.5))
        self.model_esc.add(Dense(256))
        self.model_esc.add(Activation('relu'))
        self.model_esc.add(Dropout(0.5))
        self.model_esc.add(Dense(num_labels))
        self.model_esc.add(Activation('softmax'))

        # compile model
        self.model_esc.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')

        # pre training accuracy
        score = self.model_esc.evaluate(X_esc_test, y_esc_test, verbose=0)
        accuracy = 100*score[1]
        print("Pre-training accuracy: %.4f%%" % accuracy)

        # training model
        num_epochs = 100
        num_batch_size = 32
        self.model_esc.fit(X_esc_train, y_esc_train, batch_size=num_batch_size, epochs=num_epochs, validation_data=(X_esc_test, y_esc_test), verbose=1)

        # Evaluating the model on the training and testing set
        score = self.model_esc.evaluate(X_esc_train, y_esc_train, verbose=0)
        print("Training Accuracy: {0:.2%}".format(score[1]))

        score = self.model_esc.evaluate(X_esc_test, y_esc_test, verbose=0)
        print("Testing Accuracy: {0:.2%}".format(score[1]))

    # trains a model for the Coughvid dataset
    def train_cv(self, df_cv_feat):
        X_cv = np.array(df_cv_feat.feature.tolist())
        y_cv = np.array(df_cv_feat.label.tolist())

        yy_cv = to_categorical(self.le_cv.fit_transform(y_cv))

        # split dataset
        X_cv_train, X_cv_test, y_cv_train, y_cv_test = train_test_split(X_cv, yy_cv, test_size=0.2, random_state=10)

        num_labels = yy_cv.shape[1]

        # building neural network
        self.model_cv.add(Dense(256))
        self.model_cv.add(Activation('relu'))
        self.model_cv.add(Dropout(0.5))
        self.model_cv.add(Dense(256))
        self.model_cv.add(Activation('relu'))
        self.model_cv.add(Dropout(0.5))
        self.model_cv.add(Dense(num_labels))
        self.model_cv.add(Activation('softmax'))

        # compile model
        self.model_cv.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')

        # pre training accuracy
        score = self.model_cv.evaluate(X_cv_test, y_cv_test, verbose=0)
        accuracy = 100*score[1]
        print("Pre-training accuracy: %.4f%%" % accuracy)

        # training model
        num_epochs = 100
        num_batch_size = 32
        self.model_cv.fit(X_cv_train, y_cv_train, batch_size=num_batch_size, epochs=num_epochs, validation_data=(X_cv_test, y_cv_test), verbose=1)

        # Evaluating the model on the training and testing set
        score = self.model_cv.evaluate(X_cv_train, y_cv_train, verbose=0)
        print("Training Accuracy: {0:.2%}".format(score[1]))

        score = self.model_cv.evaluate(X_cv_test, y_cv_test, verbose=0)
        print("Testing Accuracy: {0:.2%}".format(score[1]))

    # saves trained models in local files
    def save_models(self, dir_path):
        print('Saving models...')
        model_path = f'{dir_path}/models'
        if not os.path.isdir(model_path):
            os.mkdir(model_path)

        self.save_esc(model_path)
        self.save_cv(model_path)
        
        print('Models saved.')

    # saves the esc50 model in local files
    def save_esc(self, dir_path):
        if not os.path.isdir(f'{dir_path}/esc50_model'):
            os.makedirs(f'{dir_path}/esc50_model')
        self.model_esc.save(f'{dir_path}/esc50_model')

        np.save(f'{dir_path}/le_esc50.npy', self.le_esc.classes_)

    # saves the coughvid model in local files
    def save_cv(self, dir_path):
        if not os.path.isdir(f'{dir_path}/cv_model'):
            os.makedirs(f'{dir_path}/cv_model')
        self.model_cv.save(f'{dir_path}/cv_model')

        np.save(f'{dir_path}/le_cv.npy', self.le_cv.classes_)

    # loads trained models from local files
    # def load_models(self, dir_path):
    #     print('Loading models...')
    #     model_path = f'{dir_path}/models'
        
    #     self.model_esc = keras.models.load_model(f'{model_path}/esc50_model')
    #     self.model_cv = keras.models.load_model(f'{model_path}/cv_model')

    #     print('Models loaded.')

    # loads trained ESC50 model
    def load_esc(self, dir_path):
        print('Loading ESC50 Model...')
        self.model_esc = keras.models.load_model(f'{dir_path}/esc50_model')
        self.le_esc.classes_ = np.load(f'{dir_path}/le_esc50.npy')
        print('Model loaded.')

    # loads trained coughvid model
    def load_cv(self, dir_path):
        print('Loading Coughvid Model...')
        self.model_cv = keras.models.load_model(f'{dir_path}/cv_model')
        self.le_cv.classes_ = np.load(f'{dir_path}/le_cv.npy')
        print('Model loaded.')

    def predict_cough(self, file, parent):
        filepath = f'{parent}\{file}'
        print(filepath)
        processed = generateMFCC(filepath)
        processed = np.array([processed])

        # predict if there is cough
        prediction_cough = self.model_esc.predict_on_batch(processed)
        # print(prediction_cough)
        classes = np.argmax(prediction_cough, axis=1)
        # print(classes)
        # print(self.le_esc.classes_[classes])

        # predict if there is covid
        prediction_covid = self.model_cv.predict_on_batch(processed)
        # print(prediction_covid)
        classes_cv = np.argmax(prediction_covid, axis=1)
        # print(classes_cv)
        print(self.le_cv.classes_[classes_cv])

        return classes_cv[0]
