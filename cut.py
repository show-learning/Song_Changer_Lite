import os
from pychorus import find_and_output_chorus
def song_cutter(Chrous_filename, sec):
    chorus_start_sec = find_and_output_chorus(Chrous_filename, "chrous.wav", sec)
    print(chorus_start_sec)
    os.system("spleeter separate -o audio_output chrous.wav")
    if os.path.isfile("chrous.wav"):
        return True
    else:
        return False