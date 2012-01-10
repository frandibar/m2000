#-------------------------------------------------------------------------------
# Copyright (C) 2011 Francisco Dibar

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------

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

    def safe_get(self, key):
        try:
            return self.get(key)
        except ConfigParser.NoOptionError, e:
            return None

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

