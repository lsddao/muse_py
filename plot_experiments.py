import trackdata
import eegrecorder

import plotly.offline as py
import plotly.graph_objs as go

import pprint
import png
import colormap
import numpy as np

def plot_track(track_data, file_name, function):
    x_data = []
    y_data = dict()

    for x in track_data:
        x_data.append(x["ts"])
        values = trackdata.good_values(function(x))
        for var_name in values:
            if var_name not in y_data:
                y_data[var_name] = []
            y_data[var_name].append(values[var_name])

    
    data = []
    for var_name in y_data:
        trace = go.Scatter(x = x_data, y = y_data[var_name], name = var_name)
        data.append(trace)

    py.plot(data, filename=file_name+".html")

def plot_track_single(track_id, session_id, function):
    data = trackdata.TrackData(session_id)
    plot_track(data.track_data[track_id], "track{}".format(track_id), function)

def plot_track_all(session_id, function):
    data = trackdata.TrackData(session_id)
    track_id = 0
    for track in data.track_data:
        plot_track(track, "track{}".format(track_id), function)
        track_id += 1

def plot_pairs(track_data, file_name, target_function, source_function):
    x_data = []
    y_data = []

    for x in track_data:
        x_data.append( target_function(x) )
        y_data.append( trackdata.good_values(source_function(x))["source"] )

    trace = go.Scatter(x = x_data, y = y_data, mode = 'markers')
    data = [trace]

    py.plot(data, filename=file_name+".html")

def pairs_f(x):
    values = dict()
    values["alpha_diff"] = x["alpha_absolute"][1] - x["alpha_absolute"][2]
    values["enjoy"] = x["enjoy"]
    values["is_good"] = x["is_good"][1] and x["is_good"][2]
    return values

def plot_track_eeg(track_data, file_name, channel):
    x_data = []
    y_data = []

    for x in track_data:
        x_data.append(x["ts"])
        y_data.append(x["channel_data"][channel])

    data = []
    trace = go.Scatter(x = x_data, y = y_data)
    data.append(trace)

    py.plot(data, filename=file_name+".html")

def fft_color(sig):
    vals = []
    for f in sig:
        int_val = int(5*f)
        int_val = min(int_val, 255)
        int_val = max(int_val, 0)
        colors = []
        colors.append(int_val)
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

def fft_test(track_data, channel):
    sample_rate = 256
    max_image_len = 1024
    window = 90
    increment = int(sample_rate*(1-window/100))

    samples = []

    for x in track_data:
        samples.append(x["channel_data"][channel])

    f_max = 0
    f_min = 255

    num_samples = len(samples)
    png_arr = []
    img_idx = 0
    for i in range(0, num_samples, increment):
        end = i+sample_rate 
        if end >= num_samples:
            break
        f = fft(samples[i:end])
        f_max = max(f_max, max(f))
        f_min = min(f_min, min(f))
        f = fft_color(f)
        png_arr.append(f)
        if len(png_arr) == max_image_len:
            dump_image(png_arr, img_idx)
            png_arr = []
            img_idx += 1
    if len(png_arr) > 0:
        dump_image(png_arr, '{}_{}'.format(img_idx, channel))
    
    print(f_max)
    print(f_min)


data = trackdata.TrackData("20181111_001524", "eeg")
#plot_track_eeg(data.track_data[0], "eeg", 1)
#plot_spectrogram(data.track_data[0], 1)
for channel in eegrecorder.channels:
    fft_test(data.track_data[0], channel)