# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from importlib import machinery

# This class provides static methods to load the configuration file
class ConfigLoader(object):
    # Path to config file
    config_file = "/etc/bliss-boot/config.py"

    # Load the configuration file
    loader = machinery.SourceFileLoader("config", config_file)

    try:
        config = loader.load_module("config")
    except FileNotFoundError:
        print("Your configuration file \"" + config_file + "\" was not found!")
        quit(1)

    # Returns the configuration file as a module
    @classmethod
    def get_config(cls):
        return cls.config

    # Returns the path to the configuration file
    @classmethod
    def get_config_file(cls):
        return cls.config_file
