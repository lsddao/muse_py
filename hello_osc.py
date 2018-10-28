import argparse
import eegrecorder

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

    handler = eegrecorder.EEGDataRecorder(args.ip, args.port)
    handler.run()