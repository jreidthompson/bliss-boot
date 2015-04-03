# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

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
