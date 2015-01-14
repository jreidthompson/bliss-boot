# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

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
