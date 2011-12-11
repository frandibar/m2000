import os
import ConfigParser

class Config:
    config_file = os.path.expanduser('~/.m2000.cfg')
    section = 'm2000'

    def __init__(self):
        if not os.path.exists(self.config_file):
            self._create_config_file()

    def get(self, key):
        config = ConfigParser.ConfigParser()
        config.read(self.config_file)
        return config.get(self.section, key)

    def set(self, key, value):
        config = ConfigParser.ConfigParser()
        config.read(self.config_file)
        config.set(self.section, key, value)
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def _create_config_file(self):
        keys = {'create_db': 'yes' }

        config = ConfigParser.ConfigParser()
        config.add_section(self.section)
        for key, value in keys.items():
            config.set(self.section, key, value)

        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

