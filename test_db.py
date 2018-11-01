import pymongo
import datetime

import plotly.offline as py
import plotly.graph_objs as go

class TrackData:
    def __init__(self, session_id, collection_suffix = "elements"):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["muse"]
        col = db[session_id + "_" + collection_suffix]
        doc = col.find().sort("_id", pymongo.ASCENDING)
        self.track_data = []
        current_track = []
        for x in doc:
            if "event_name" in x:
                if len(current_track) > 0:
                    self.track_data.append(current_track)
                    current_track = []
            else:
                current_track.append(x)
        if len(current_track) > 0:
            self.track_data.append(current_track)

def plot_track(track_data, track_name, function):
    x_data = []
    y_data = dict()

    for x in track_data:
        x_data.append(x["ts"])
        values = function(x)
        for var_name in values:
            if var_name not in y_data:
                y_data[var_name] = []
            y_data[var_name].append(values[var_name])

    
    data = []
    for var_name in y_data:
        trace = go.Scatter(x = x_data, y = y_data[var_name], name = var_name)
        data.append(trace)

    py.plot(data, filename=track_name+".html")

def test_ids_and_sorting(col):
    doc = col.find().sort("_id", pymongo.ASCENDING)

    last_ts = None
    last_id = None
    count = 0

    for x in doc:
        x_id = x["_id"]
        x_ts = x["ts"]
        if last_id is not None:
            if last_id >= x_id:
                print("Sorting error: object with id {} after the object with id {}".format(x_id, last_id))
        if last_ts is not None:
            if last_ts >= x_ts:
                print("Error: object with id {} has ts >= ts of the object with id {}".format(x_id, last_id))
        last_ts = x_ts
        last_id = x_id
        count += 1

    print("Checked {} objects".format(count))

#test_ids_and_sorting(elements_col)
#plot_first(elements_col)

def values_function(x):
    values = dict()

    good = x["is_good"][1] and x["is_good"][2]

    values["alpha_diff(L-R)"] = x["alpha_absolute"][1] - x["alpha_absolute"][2]
    #values["beta_diff"] = x["beta_absolute"][1] - x["beta_absolute"][2]
    #values["gamma_diff"] = x["gamma_absolute"][1] - x["gamma_absolute"][2]
    #values["delta_diff"] = x["delta_absolute"][1] - x["delta_absolute"][2]
    #values["theta_diff"] = x["theta_absolute"][1] - x["theta_absolute"][2]

    for var_name in values:
        if not good:
            values[var_name] = None

    values["enjoy"] = x["enjoy"]
    #values["is_good"] = is_good
    return values

data = TrackData("20181029_210225")
track_id = 0
#plot_track(data.track_data[track_id], "track{}".format(track_id), values_function)
for track in data.track_data:
    plot_track(track, "track{}".format(track_id), values_function)
    track_id += 1