import numpy as np
from numpy import sin, pi
from scipy.signal import get_window
from operator import itemgetter
import matplotlib.pyplot as plt
import librosa
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft
import json
import soundfile as sf
import pathlib
#analyst change sound
def sinusoid(f, A, t):
    """
    # https://en.wikipedia.org/wiki/Sine_wave
    Input:
        f: ordinary frequency
        A: amplitude
        t: time span
    Output:
        return a sinusoid
    """
    w = 2 * pi * f      # angular frequency
    y = A * sin(w * t)  # sinusoid
    return y

def frame_data(A, f0, t0, fs, N, r1, r2, r3, r4, r5, r6, r7, r8, r9):
    """
    Input:
        A: amplitude
        f0: fundamental frequency
        t0: start time
        fs: sampling rate
        N: frame size
        r1: ratio of fundamental frequency
        r2: ratio of 1st harmonic wave
        r3: ratio of 2nd harmonic wave
        r4: ratio of 3rd harmonic wave
        r5: ratio of 4th harmonic wave
        r6: ratio of 5th harmonic wave
        r7: ratio of 6th harmonic wave
        r8: ratio of 7th harmonic wave
        r9: ratio of 8th harmonic wave
    Output:
        return data
    """
    T = 1/fs                   # sampling interval
    D = T * N                  # frame duration
    t = np.linspace(t0, D, N)  # time span
    f0w = sinusoid(f0 * 1, A, t)   # fundamental frequency wave
    h1w = sinusoid(f0 * 2, A, t)   # 1st harmonic wave
    h2w = sinusoid(f0 * 3, A, t)   # 2nd harmonic wave
    h3w = sinusoid(f0 * 4, A, t)   # 3rd harmonic wave
    h4w = sinusoid(f0 * 5, A, t)   # 4th harmonic wave
    h5w = sinusoid(f0 * 6, A, t)   # 4th harmonic wave
    h6w = sinusoid(f0 * 7, A, t)   # 4th harmonic wave
    h7w = sinusoid(f0 * 8, A, t)   # 4th harmonic wave
    h8w = sinusoid(f0 * 9, A, t)   # 4th harmonic wave
    data = f0w * r1 + h1w * r2 + h2w * r3 + h3w * r4 + h4w * r5 + h5w * r6 + h6w * r7 + h7w * r8 + h8w * r9
    return data

def sound_synthesizer(mode, inputItem, frame_size, config, output_filename):
    """
    # https://librosa.org/librosa/master/generated/librosa.core.piptrack.html
    Input:
        mode: (1) frequency as input   (2) frequency_list as input   (3) filename as input
        inputItem: filename or frequency_list or frequency
        frame_size: frame size (useless for mode 3)
        config: modify timbre
        output_filename: output filename
    Output:
        write data to output_filename
    """
    t0 = 0          # start time
    fs = 48000      # sampling rate
    N = frame_size  # frame size
    
    r1 = config['r1']
    r2 = config['r2']
    r3 = config['r3']
    r4 = config['r4']
    r5 = config['r5']
    r6 = config['r6']
    r7 = config['r7']
    r8 = config['r8']
    r9 = config['r9']
    
    if mode == 1:
        
        A = 0.5
        f0 = inputItem
        
    elif mode == 2:
        
        A = 0.5
        # f0 = [261, 293, 329, 349, 392, 440, 493, 523]   C4~C5
        f0 = inputItem
        
    elif mode == 3:
        
        A = []
        f0 = []

        y, sr = librosa.load(inputItem, sr=None)
        pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr, fmin=75, fmax=1600)
        
        for i in range(int(magnitudes.size / 1025)):
            index = magnitudes[:, i].argmax()
            pitch = pitches[index, i]
            volume = magnitudes[index, i]
            A.append(volume)
            f0.append(pitch)
        
        maximum = max(A)
        for i in range(len(A)):
            A[i] = A[i] / maximum / 2
        
    result = []
    
    if mode == 1:
        result = frame_data(A, f0, t0, fs, N, r1, r2, r3, r4, r5, r6, r7, r8, r9)
    elif mode == 2:
        for f in f0:
            result.extend(frame_data(A, f, t0, fs, N, r1, r2, r3, r4, r5, r6, r7, r8, r9))
    elif mode == 3:
        for i in range(len(A)):
            result.extend(frame_data(A[i], f0[i], t0, fs, 512, r1, r2, r3, r4, r5, r6, r7, r8, r9))
        
    result = np.array(result)
    
    if mode == 3:
        write(output_filename, sr, result)
    else:
        write(output_filename, fs, result)
def cut_frames(data, frame_size, hop_size, window):         #切音框來分析
  """
  """
  overlap = frame_size - hop_size       #hop_size = 1/3 frame_size => overlap 是 2/3 frame_size
  num_frame = (data.size - overlap) // hop_size     #//向小取整
  frames = []
  cur = overlap
  i = 0
  while i < num_frame:
      cur = cur - overlap
      j = 0
      frame = np.zeros(frame_size)
      while j < frame_size:
          frame[j] = data[cur]
          cur = cur + 1
          j = j + 1
      i = i + 1
      frame = frame * get_window(window, frame_size)
      frames.append(frame)
  frames = np.array(frames)

  return frames, num_frame

def change_timbre(spectrum, num_frames, frame_size, option):        #改變音色
    """
    """
    precision = 5
    new_spectrum = []
    #print(num_frames)
    for j in range(num_frames):
        X = abs(spectrum[j])
        #print(X)
        Y = spectrum[j]
        # https://stackoverflow.com/questions/4624970/finding-local-maxima-minima-with-numpy-in-a-1d-numpy-array
        local_maximum = np.r_[True, X[1:] > X[:-1]] & np.r_[X[:-1] > X[1:], True]
        #print(len(local_maximum))
        local_maximum_list = []
        for i in range(len(local_maximum)//2):
            if local_maximum[i] == True:
                local_maximum_list.append((i, X[i]))
        # https://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
        # https://stackoverflow.com/questions/13145368/find-the-maximum-value-in-a-list-of-tuples-in-python
        wow = sorted(local_maximum_list, key=itemgetter(1), reverse=True)
        boss = max(wow, key=itemgetter(1))
        lowest = boss[0]
        for i in range(precision):
            if wow[i][0] < boss[0] and wow[i][1] >= boss[1] / 2:
                lowest = wow[i][0]

        new_X = np.zeros(Y.size)
        new_X[lowest] = Y[lowest]

        # ==================================================

        if option == 1:
            # trumpet
            new_X[lowest*2] = new_X[lowest] * 25.19 / 18.03
            new_X[lowest*3] = new_X[lowest] * 28.12 / 18.03
            new_X[lowest*4] = new_X[lowest] * 16.00 / 18.03
            new_X[lowest*5] = new_X[lowest] * 4.91 / 18.03
            new_X[lowest*6] = new_X[lowest] * 2.74 / 18.03
            new_X[lowest*7] = new_X[lowest] * 2.73 / 18.03
            new_X[lowest*8] = new_X[lowest] * 1.48 / 18.03
            # new_X[lowest*9] = new_X[lowest] * 0.80 / 18.03
        elif option == 2:
            # oboe
            new_X[lowest*2] = new_X[lowest] * 50.92 / 14.62
            new_X[lowest*3] = new_X[lowest] * 21.34 / 14.62
            new_X[lowest*4] = new_X[lowest] * 7.71 / 14.62
            new_X[lowest*5] = new_X[lowest] * 1.72 / 14.62
            new_X[lowest*6] = new_X[lowest] * 2.78 / 14.62
            new_X[lowest*7] = new_X[lowest] * 0.15 / 14.62
            new_X[lowest*8] = new_X[lowest] * 0.70 / 14.62
            new_X[lowest*9] = new_X[lowest] * 0.07 / 14.62
        elif option == 3:
            # marimba
            new_X[lowest*2] = new_X[lowest] * 13.60 / 85.72
        elif option == 4:
            # organ
            new_X[lowest*2] = new_X[lowest] * 13.38 / 22.71
            new_X[lowest*3] = new_X[lowest] * 15.12 / 22.71
            new_X[lowest*4] = new_X[lowest] * 15.36 / 22.71
            new_X[lowest*5] = new_X[lowest] * 0.97 / 22.71
            new_X[lowest*6] = new_X[lowest] * 26.22 / 22.71
            new_X[lowest*7] = new_X[lowest] * 0.49 / 22.71
            new_X[lowest*8] = new_X[lowest] * 3.96 / 22.71
            new_X[lowest*9] = new_X[lowest] * 1.79 / 22.71
        elif option == 5:
            # glockenspiel
            new_X[lowest*3] = new_X[lowest] * 62.06 / 27.56
            new_X[lowest*6] = new_X[lowest] * 7.56 / 27.56
            new_X[lowest*9] = new_X[lowest] * 2.34 / 27.56
        elif option == 6:
            # pure
            None
        elif option == 7:
            with open('data.txt') as json_file:
                data = json.load(json_file)
            new_X[lowest*2] = new_X[lowest] * data['r2'] / data['r1']
            new_X[lowest*3] = new_X[lowest] * data['r3'] / data['r1']
            new_X[lowest*4] = new_X[lowest] * data['r4'] / data['r1']
            new_X[lowest*5] = new_X[lowest] * data['r5'] / data['r1']
            new_X[lowest*6] = new_X[lowest] * data['r6'] / data['r1']
            new_X[lowest*7] = new_X[lowest] * data['r7'] / data['r1']
            new_X[lowest*8] = new_X[lowest] * data['r8'] / data['r1']
            new_X[lowest*9] = new_X[lowest] * data['r9'] / data['r1']
        
        new_spectrum.append(new_X)
    
    new_spectrum = np.array(new_spectrum)
    return new_spectrum
def song_changer(filename):
    fs, x = read(filename)
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
    frame_size = 2**14
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
    return str(pathlib.Path(__file__).parent.absolute())
