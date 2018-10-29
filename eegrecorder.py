import pymongo
import datetime

from pythonosc import dispatcher
from pythonosc import osc_server

class EEGDataRecorder:
    def __init__(self, variables_provider, osc_ip = "127.0.0.1", osc_port = 7000, db_connection = "mongodb://localhost:27017/"):
        self._variables_provider = variables_provider
        self._session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self._subject_data = dict()
        self.init_db(db_connection)
        self._dispatcher = dispatcher.Dispatcher()
        self.map_handlers()
        self._server = osc_server.ThreadingOSCUDPServer((osc_ip, osc_port), self._dispatcher)
        self._doc = dict()

    def init_db(self, db_connection):
        db_client = pymongo.MongoClient(db_connection)
        db = db_client["muse"]
        self._eeg_col = db[self._session_id + "_eeg"]
        self._elements_col = db[self._session_id + "_elements"]
        self._session_col = db["sessions"]

    def record_eeg(self):
        self._dispatcher.map("/notch_filtered_eeg", self.handler_eeg)

    def map_handlers(self):
        self._dispatcher.map("/elements/alpha_absolute", self.handler_elements)
        self._dispatcher.map("/elements/beta_absolute", self.handler_elements)
        self._dispatcher.map("/elements/gamma_absolute", self.handler_elements)
        self._dispatcher.map("/elements/delta_absolute", self.handler_elements)
        self._dispatcher.map("/elements/theta_absolute", self.handler_elements)
        self._dispatcher.map("/elements/is_good", self.handler_elements)
        self._dispatcher.map("/elements/horseshoe", self.handler_elements)
        self._handlers_count = 7

    def stop(self):
        self._server.shutdown()
        self.write_session_end()

    def run(self):
        print("Serving on {}".format(self._server.server_address))
        self.write_session_begin()
        self._server.serve_forever()

    def set_subject_data(self, subject_data):
        self._subject_data = subject_data

    def trigger_event(self, event_name):
        doc = {
            "event_name" : event_name,
            "ts" : datetime.datetime.now()
        }
        self._elements_col.insert_one(doc)

    def write_session_begin(self):
        doc = {
            "session_id": self._session_id,
            "subject_name": self._subject_data["name"],
            "begin" : datetime.datetime.now()
        }
        self._session_col.insert_one(doc)
        print("Session {} with {} started".format(self._session_id, self._subject_data["name"]))

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

    def handler_elements(self, addr, ch1, ch2, ch3, ch4):
        element = addr.replace("/elements/", "")
        if element != "alpha_absolute" and len(self._doc) == 0:
            return  # write only full bundles
        self._doc[element] = [ch1, ch2, ch3, ch4]
        if len(self._doc) == self._handlers_count:
            self.dump_to_db()
 
    def dump_to_db(self):
        self._doc.update(self._variables_provider.getVariables())
        self._doc["ts"] = datetime.datetime.now()
        self._elements_col.insert_one(self._doc)
        self._doc = dict()