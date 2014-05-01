# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from importlib import machinery

class ConfigLoader:
	# Path to config file
	config_file = "/etc/bliss-boot/conf.py"

	# Load the configuration file
	loader = machinery.SourceFileLoader("config", config_file)
	config = loader.load_module("config")

	# Returns the conf.py module
	def get_config():
		return ConfigLoader.config

	# Returns the path to the config file
	def get_config_file():
		return ConfigLoader.config_file
