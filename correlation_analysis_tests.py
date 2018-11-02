import trackdata
import eegrecorder

import pprint

def good_values(values):
    if "is_good" in values:
        good = values["is_good"]
        values.pop("is_good")
        if not good:
            for var_name in values:
                values[var_name] = None
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

channel_combinations = [ [1,2]  ]

fitness_functions = dict()

for band in eegrecorder.bands:
    for channel in eegrecorder.channels:
        fitness_functions["fintess_absolute_" + band + str(channel)] = lambda x, band=band, channel=channel: fintess_absolute(x, band, channel)

for band in eegrecorder.bands:
    for channel in channel_combinations:
        fitness_functions["fintess_diff_" + band + str(channel[0])+str(channel[1])] = lambda x, band=band, ch1=channel[0], ch2=channel[1]: fitness_diff(x, band, ch1, ch2)

data = trackdata.TrackData("20181029_210225")
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