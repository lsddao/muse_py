import pymongo

class DBConnection:
    def __init__(self, session_id, collection_suffix):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["muse"]
        col = db[session_id + "_" + collection_suffix]
        self.doc = col.find().sort("_id", pymongo.ASCENDING)

class TrackData:
    def __init__(self, session_id, collection_suffix):
        dbconn = DBConnection(session_id, collection_suffix)
        self.track_data = []
        current_track = []
        for x in dbconn.doc:
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

# not needed anymore?
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