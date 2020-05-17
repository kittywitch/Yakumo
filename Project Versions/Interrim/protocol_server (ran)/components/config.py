import os, logging, json, components.modularity

class Config():
    def __init__(self):
        raw = self.load()
        self.raw = raw
        if "connection" in raw:
            if "port" in raw["connection"]:
                if isinstance(raw["connection"]["port"], int):
                    self.port = raw["connection"]["port"]
                else:
                    logging.error("Port should be specified as an integer.")
            else:
                logging.error("Config file is missing 'raw[\"connection\"][\"port\"].")
            if "api" in raw["connection"]:
                if isinstance(raw["connection"]["api"], str):
                    self.api = raw["connection"]["api"]
                else:
                    logging.error("API hostname should be specified as a string.")
            else:
                logging.error("Config file is missing 'raw[\"connection\"][\"api\"].")
        else:
            logging.error("Config file is missing 'raw[\"connection\"].")
        if "pushover" in raw:
            if "token" in raw["pushover"] and isinstance(raw["pushover"]["token"], str) and "user" in raw["pushover"] and isinstance(raw["pushover"]["user"], str):
                logging.info("Pushover integration enabled.")
                self.pushover = raw["pushover"]

    def load(self):
        if os.path.exists("./data"):
            if os.path.exists("./data/config.json"):
                with open('./data/config.json') as jf:
                    raw_config = json.load(jf)
                    logging.info(f"Loaded the config from {os.path.join(components.modularity.base_path, 'data/config.json')}.")
                    return raw_config
            else:
                logging.error(f"File {os.path.join(components.modularity.base_path, 'data/config.json')} not found.")
        else:
            logging.error(f"Directory {os.path.join(components.modularity.base_path, 'data')} not found.")

def init():
    global config
    config = Config()