import pymongo
import trackdata

import plotly.offline as py
import plotly.graph_objs as go

import pprint

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

def values_function(x):
    values = dict()
    values["alpha_absolute_L"] = x["alpha_absolute"][1]
    values["alpha_absolute_R"] = x["alpha_absolute"][2]

    values["alpha_diff"] = x["alpha_absolute"][1] - x["alpha_absolute"][2]
    values["beta_diff"] = x["beta_absolute"][1] - x["beta_absolute"][2]
    values["gamma_diff"] = x["gamma_absolute"][1] - x["gamma_absolute"][2]
    values["delta_diff"] = x["delta_absolute"][1] - x["delta_absolute"][2]
    values["theta_diff"] = x["theta_absolute"][1] - x["theta_absolute"][2]

    values["enjoy"] = x["enjoy"]
    values["is_good"] = x["is_good"][1] and x["is_good"][2]
    return values

def plot_track_single(track_id, session_id):
    data = trackdata.TrackData(session_id)
    plot_track(data.track_data[track_id], "track{}".format(track_id), values_function)

def plot_track_all(session_id):
    data = trackdata.TrackData(session_id)
    track_id = 0
    for track in data.track_data:
        plot_track(track, "track{}".format(track_id), values_function)
        track_id += 1

session_id = "20181029_210225"
track_ids = [12, 15]

plot_track_single(track_ids[0], session_id)
plot_track_single(track_ids[1], session_id)