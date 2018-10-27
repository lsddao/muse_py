import argparse
import math
import pymongo
import datetime

from pythonosc import dispatcher
from pythonosc import osc_server

class EEGDataRecorder:
    def __init__(self, osc_ip, osc_port, db_connection, subject_name = "dummy"):
        self._session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self._subject_name = subject_name
        self.init_db(db_connection)
        self._dispatcher = dispatcher.Dispatcher()
        self.map_handlers()
        self._server = osc_server.ThreadingOSCUDPServer((osc_ip, osc_port), self._dispatcher)
        self._doc = dict()

    def __del__(self):
        self.stop()

    def init_db(self, db_connection):
        db_client = pymongo.MongoClient(db_connection)
        db = db_client["muse"]
        self._eeg_col = db[self._session_id + "_eeg"]
        self._elements_col = db[self._session_id + "_elemets"]
        self._session_col = db["sessions"]

    def map_handlers(self):
        #self._dispatcher.map("/notch_filtered_eeg", self.handler_eeg)
        self._dispatcher.map("/elements/alpha_absolute", self.handler_alpha)
        self._dispatcher.map("/elements/beta_absolute", self.handler_beta)
        self._dispatcher.map("/elements/gamma_absolute", self.handler_gamma)
        self._dispatcher.map("/elements/delta_absolute", self.handler_delta)
        self._dispatcher.map("/elements/theta_absolute", self.handler_theta)
        self._dispatcher.map("/elements/is_good", self.handler_is_good)
        self._dispatcher.map("/elements/horseshoe", self.handler_horseshoe)

    def stop(self):
        self._server.shutdown()
        self.write_session_end()

    def run(self):
        print("Serving on {}".format(self._server.server_address))
        self.write_session_begin()
        self._server.serve_forever()

    def write_session_begin(self):
        doc = {
            "session_id": self._session_id,
            "subject_name": self._subject_name,
            "begin" : datetime.datetime.now()
        }
        self._session_col.insert_one(doc)
        print("Session {} with subject {} started".format(self._session_id, self._subject_name))

    def write_session_end(self):
        doc = {
            "session_id": self._session_id,
            "end" : datetime.datetime.now()
        }
        self._session_col.insert_one(doc)
        print("Session {} ended".format(self._session_id))

    def handler_eeg(self, unused_addr, ch1, ch2, ch3, ch4):
        doc = {
            "channel_data" : [ch1, ch2, ch3, ch4],
        }
        self._eeg_col.insert_one(doc)

    def handler_alpha(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["alpha"] = [ch1, ch2, ch3, ch4]

    def handler_beta(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["beta"] = [ch1, ch2, ch3, ch4]

    def handler_gamma(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["gamma"] = [ch1, ch2, ch3, ch4]

    def handler_delta(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["delta"] = [ch1, ch2, ch3, ch4]

    def handler_theta(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["theta"] = [ch1, ch2, ch3, ch4]

    def handler_is_good(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["is_good"] = [ch1, ch2, ch3, ch4]

    def handler_horseshoe(self, unused_addr, ch1, ch2, ch3, ch4):
        self._doc["horseshoe"] = [ch1, ch2, ch3, ch4]
        # last handler writes data to db
        self._elements_col.insert_one(self._doc)
        self._doc = dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=7000,
                        help="The port to listen on")
    args = parser.parse_args()

    handler = EEGDataRecorder(args.ip, args.port, "mongodb://localhost:27017/")
    handler.run()