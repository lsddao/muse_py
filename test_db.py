import pymongo
import datetime

import plotly.offline as py
import plotly.graph_objs as go

import pprint

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

def good_values(values):
    if "is_good" in values:
        good = values["is_good"]
        values.pop("is_good")
        if not good:
            for var_name in values:
                values[var_name] = None
    return values

def plot_track(track_data, file_name, function):
    x_data = []
    y_data = dict()

    for x in track_data:
        x_data.append(x["ts"])
        values = good_values(function(x))
        for var_name in values:
            if var_name not in y_data:
                y_data[var_name] = []
            y_data[var_name].append(values[var_name])

    
    data = []
    for var_name in y_data:
        trace = go.Scatter(x = x_data, y = y_data[var_name], name = var_name)
        data.append(trace)

    py.plot(data, filename=file_name+".html")

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
    values["alpha_absolute_L"] = x["alpha_absolute"][1]
    values["alpha_absolute_R"] = x["alpha_absolute"][2]

    #values["alpha_diff(L-R)"] = x["alpha_absolute"][1] - x["alpha_absolute"][2]
    #values["beta_diff"] = x["beta_absolute"][1] - x["beta_absolute"][2]
    #values["gamma_diff"] = x["gamma_absolute"][1] - x["gamma_absolute"][2]
    #values["delta_diff"] = x["delta_absolute"][1] - x["delta_absolute"][2]
    #values["theta_diff"] = x["theta_absolute"][1] - x["theta_absolute"][2]

    values["enjoy"] = x["enjoy"]
    values["is_good"] = x["is_good"][1] and x["is_good"][2]
    return values

def fitness_target(x):
    return x["enjoy"]

def fintess_absolute(x, band, channel):
    return {
        "source" : x[band + "_absolute"][channel],
        "is_good" : x["is_good"][channel] == 1
    }

def fitness_diff(x, band, channel1, channel2):
    b = band + "_absolute"
    return {
    "source" : x[b][channel1] - x[b][channel2],
    "is_good" : x["is_good"][channel1] and x["is_good"][channel2]
    }

bands = ["alpha", "beta", "gamma", "delta", "theta"]
#channels = [0, 1, 2, 3]
channels = [1, 2]
#channel_combinations = [ [0,1], [0,2], [0,3], [1,2], [1,3], [2,3]  ]
channel_combinations = [ [1,2]  ]

fitness_functions = dict()

for band in bands:
    for channel in channels:
        fitness_functions["fintess_absolute_" + band + str(channel)] = lambda x, band=band, channel=channel: fintess_absolute(x, band, channel)

for band in bands:
    for channel in channel_combinations:
        fitness_functions["fintess_diff_" + band + str(channel[0])+str(channel[1])] = lambda x, band=band, ch1=channel[0], ch2=channel[1]: fitness_diff(x, band, ch1, ch2)

data = TrackData("20181029_210225")
track_id = 0
stats = dict()

for f_name in fitness_functions:
    count_all = 0
    count_good = 0
    fitness = 0
    for track in data.track_data:
        for doc in track:
            target = fitness_target(doc)
            values = fitness_functions[f_name](doc)
            source = good_values(values)["source"]
            if source is not None:
                fitness += abs(source - target)
                count_good += 1
            count_all += 1
        track_id += 1
    stats[f_name] = {
        "fitness" : fitness / count_good,
        "good %" : int(100*count_good/count_all)
    }
    
pprint.pprint(stats)

#data = TrackData("20181029_210225")
#track_id = 0
#plot_track(data.track_data[track_id], "track{}".format(track_id), values_function)
#for track in data.track_data:
#    plot_track(track, "track{}".format(track_id), values_function)
#    track_id += 1