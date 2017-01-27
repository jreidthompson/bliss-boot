# Copyright 2014-2017 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
