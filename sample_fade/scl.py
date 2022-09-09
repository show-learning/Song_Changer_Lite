import numpy as np
import matplotlib.pyplot as plt
import librosa
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft
from my_toolbox import cut_frames, change_timbre
from synthesizer import sound_synthesizer
import json
import soundfile as sf
import os
from pychorus import find_and_output_chorus
#get chrous
print("Please input your filepath to get song")
Chrous_filename = input()
print("Please input how much time you want get")
sec = int(input())
chorus_start_sec = find_and_output_chorus(Chrous_filename, "chrous.wav", sec)
os.system("spleeter separate -o audio_output chrous.wav")
#analyst change sound
print("Please input your filepath to get sound")
Sound_filename = input()
fs, x = read(Sound_filename)
X = fft(x[:10000])
abs_X = abs(X)
"""
get sound feature
"""
plt.plot(x[3000:3500])
f = np.linspace(0, fs, 10000)
plt.plot(f, abs_X)
plt.xlim([0,5000])
temp_list = []
for i in range(40):
    if max(abs_X[50*i:50*i+49]) > max(abs_X) * 1/22:
        temp_list.append(50*i + np.argmax(abs_X[50*i:50*i+49]))
my_list = []
my_list.append(temp_list[0])
for i in range(1,len(temp_list)):
    if temp_list[i] - temp_list[i-1] >= 20:
        my_list.append(temp_list[i])
r = [ 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9' ]
timbre_config = {}
total = sum(abs_X[my_list])
for i in range(9):
    if i < len(my_list):
        timbre_config[r[i]] = abs_X[my_list[i]] / total
    else:
        timbre_config[r[i]] = 0

frequency = fs / 10000 * my_list[0]
sound_synthesizer(1, frequency, 48000, timbre_config, 'sound.wav')
"""
prepare data.txt
"""
with open('data.txt', 'w') as outfile:
    json.dump(timbre_config, outfile)
#sound changer
fs, data = read('./audio_output/chrous/vocals.wav')
# if double channel choose left channel
if data.shape[0] > 1:
    data = data[:,0]
"""
cut frames ＆ windowing
https://blog.csdn.net/u010592995/article/details/81001751
https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.check_COLA.html
"""
#change frame size to fit the frame
frame_size = 2**12
#try change window function
window = 'hann'
hop_size = int(frame_size * 1/3)
frames, num_frames = cut_frames(data, frame_size, hop_size, window)
"""
FFT to spectrum
"""
spectrum = []
for i in range(num_frames):
    X = fft(frames[i])
    spectrum.append(X)
spectrum = np.array(spectrum)
new_spectrum = change_timbre(spectrum, num_frames, frame_size,option=7)
"""
back to time domain
"""
new_frames = []
for i in range(num_frames):
    x = ifft(new_spectrum[i])
    new_frames.append(x)
new_frames = np.array(new_frames)
"""
overlap the frames
"""
new_data = np.zeros(data.size)
i = 0
for j in range(num_frames):
    for k in range(frame_size):
        new_data[i] = new_data[i] + new_frames[j,k]
        i = i + 1
    i = i - (frame_size - hop_size)
new_data = new_data / max(abs(new_data)) * 0.5   # limit the volume
write('output.wav', fs, new_data)
print("Success")
vocal, sr1 = sf.read("output.wav")
accompany, sr2 = sf.read("./audio_output/chrous/accompaniment.wav")
if accompany.shape[0] > 1:
    final_output = vocal + accompany[:,0]
else:
    final_output = vocal + accompany
sf.write('plus.wav',final_output,sr1)
plt.plot(new_data[:frame_size*30])
