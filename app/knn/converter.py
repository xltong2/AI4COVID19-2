'''
Helper file to convert Coughvid dataset audio files from ogg/webm to wav
The converted files will be placed in ./audio_coughvid

Before running this file, make sure to download the coughvid dataset from: https://zenodo.org/record/4498364
Place the public_dataset folder into the same directory as this file
The user's system also needs to have FFMPEG installed for this script to function
'''

import numpy as np
import pandas as pd
import subprocess

import os
import os.path
from os import path

# this file's path
# file has to be in the ai4c19 directory
dir_path = os.path.dirname(os.path.realpath(__file__))

# coughvid folder path
coughvid_path = f'{dir_path}/public_dataset'

# wav folder path
coughvid_wav_path = f'{dir_path}/audio_coughvid'
if (not path.exists(coughvid_wav_path)):
    os.mkdir(coughvid_wav_path)
    
# read csv metadata_compiled
df = pd.read_csv(f'{dir_path}/dataset_metas/metadata_compiled.csv')

# convert all webm and ogg files to wav
filenames = df.uuid.to_numpy()
for counter, name in enumerate(filenames):
    if (path.isfile(f'{coughvid_path}/{name}.webm')):
        # convert from webm to wav
        # put wav in new folder
        subprocess.call(["ffmpeg", "-i", f'{coughvid_path}/{name}.webm', f'{coughvid_wav_path}/{name}.wav'])
    elif (path.isfile(f'{coughvid_path}/{name}.ogg')):
        # convert from ogg to wav
        # put wav in new folder
        subprocess.call(["ffmpeg", "-i", f'{coughvid_path}/{name}.ogg', f'{coughvid_wav_path}/{name}.wav'])
    else:
        print(f'Error, no file found: {name}')
    print(f'Finished {counter}/{len(filenames)}')