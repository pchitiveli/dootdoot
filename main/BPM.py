import librosa
import numpy as np
import sys
import os

test_path = os.getcwd() + "\\tests\\WAVs (Raw Audio)\\trumpetTest4.wav"

time_series, sampling_rate = librosa.load(test_path)
tempo, beats = librosa.beat.beat_track(y=time_series, sr=sampling_rate)
print(tempo[0])

