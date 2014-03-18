# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import string

from subprocess import call
from importlib import machinery

from . import other

# Path to config file
config_loc = "/etc/bliss-boot/conf.py"

# Explictly load the conf file without using the 'get_conf' function
loader = machinery.SourceFileLoader("conf", config_loc)
conf = loader.load_module("conf")

class Toolkit(object):
	def print_info(self):
		self.ewarn("---------------------------")
		self.ewarn("| " + other.pname + " - v" + other.pversion)
		self.ewarn("| Author: " + other.pcontact)
		self.ewarn("| Distributed under the " + other.plicense)
		self.ewarn("---------------------------")

	# Cleanly exit the application
	def die(self, message):
		call(["echo", "-e", "\e[1;31m" + message + "\e[0;m"])

		# Remove the incomplete bootloader file
		if conf.bootloader == "grub2":
			if os.path.exists("grub.cfg"):
				os.remove("grub.cfg")
		elif conf.bootloader == "extlinux":
			if os.path.exists("extlinux.conf"):
				os.remove("extlinux.conf")
		elif conf.bootloader == "lilo":
			if os.path.exists("lilo.conf"):
				os.remove("lilo.conf")

		quit(5)

	# Get the index for a letter in the alphabet
	def get_alph_index(self, letter):
		alphabet = string.ascii_lowercase

		count = 0

		for let in alphabet:
			if let == letter:
				return count

			count = count + 1

	# Find values in common from two lists and return a third list
	def find_common_kernels(self, list_a, list_b):
		common_list = []

		for a in list_a:
			for b in list_b:
				if a == b:
					common_list.append(a)

		return common_list

	# Strips the first directory of the path passed. Used to get a good path and not need
	# a boot symlink in /boot
	def strip_head(self, path):
		if path:
			splinters = path.split("/")
			srange = len(splinters)

			if srange >= 3:
				news = ""

				for i in range(len(splinters))[2:]:
					news = news + "/" + splinters[i]

				return news
			elif srange == 2:
				# if two then that means we will be looking in that folder specifically for kernels
				# so just return /
				return "/"
		else:
			self.die("The value to strip is empty ...")

	# Prints a message with the module name included
	def eprint(self, x):
		call(["echo", "-e", "\e[1;36m" + x + "\e[0;m "])

	# Used for successful entries
	def esucc(self, x):
		call(["echo", "-e", "\e[1;32m" + x + "\e[0;m"])

	# Used for warnings
	def ewarn(self, x):
		call(["echo", "-e", "\e[1;33m" + x + "\e[0;m "])

	# Returns the conf.py module
	def get_conf(self):
		loader = machinery.SourceFileLoader("conf", config_loc)
		conf = loader.load_module("conf")
		return conf

	# Returns the path to the config file
	def get_conf_file(self):
		return config_loc
