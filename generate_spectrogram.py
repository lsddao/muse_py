import trackdata
import eegrecorder

import pprint
import png
import colormap
import numpy as np
import collections

def int_val(f):
    v = int(5*f)
    v = min(v, 255)
    v = max(v, 0)
    return v

def fft_color(sig):
    vals = []
    for i in range(len(sig)):
        colors = []
        v = int_val(sig[i])
        colors.append(v)
        vals.append(colors)
    return vals

def fft(sig):
    win = np.hanning(len(sig))
    samples = np.array(sig, dtype='float64')
    samples *= win
    f = abs(np.fft.rfft(samples, norm='ortho')).tolist()[1:]
    f = np.array(f)
    return f

def dump_image(arr, image_name):
    png.from_array(arr, 'L').save("tmp\\{}.png".format(image_name))

def generate_slices(session_id, channel, sample_rate=256, max_image_len=128, window=90):
    dbconn = trackdata.DBConnection(session_id, 'eeg')
    increment = int(sample_rate*(1-window/100))

    samples = collections.deque(maxlen=sample_rate)

    shift = 0
    png_arr = []
    img_idx = 0
    enjoy = 0
    for x in dbconn.doc:
        if "channel_data" in x:
            U = x["channel_data"][channel]
            if len(samples) == samples.maxlen:
                shift += 1
            samples.append(U)
            if shift == increment:
                shift = 0
                f = fft(samples)
                png_arr.append(fft_color(f))
            if len(png_arr) == max_image_len:
                dump_image(png_arr, '{}_{}_ch{}_enjoy{}'.format(session_id, img_idx, channel, enjoy))
                png_arr = []
                img_idx += 1
        elif "event_name" in x:
            if x["event_name"] == "enjoy_changed":
                enjoy = x["value"]

generate_slices("20181117_193958", 1)