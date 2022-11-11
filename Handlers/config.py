import configparser


class ConfigHandler:
    def __init__(self, path=None):
        self.config = configparser.RawConfigParser()
        self.config.read(path if path != None else './config.ini')

    def get_key(self, section, option):
        return str(self.config.get(section, option))
