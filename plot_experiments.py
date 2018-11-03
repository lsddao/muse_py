import trackdata

import plotly.offline as py
import plotly.graph_objs as go

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