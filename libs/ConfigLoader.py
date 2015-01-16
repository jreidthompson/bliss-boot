# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from importlib import machinery

# This module provides static methods to load the configuration file

# Path to config file
configFilePath = "/etc/bliss-boot/config.py"

# Load the configuration file
loader = machinery.SourceFileLoader("config", configFilePath)

try:
    configModule = loader.load_module("config")
except FileNotFoundError:
    print("Your configuration file \"" + configFilePath + "\" was not found!")
    quit(1)

# Returns the configuration file as a module
def GetConfigModule():
    return configModule

# Returns the path to the configuration file
def GetConfigFilePath():
    return configFilePath
