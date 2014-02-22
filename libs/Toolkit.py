# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import string

from subprocess import call

from etc import conf
from etc import other

class Toolkit(object):
	def print_info(self):
		self.ewarn("---------------------------")
		self.ewarn("| " + other.pname + " - v" + other.pversion)
		self.ewarn("| Author: " + other.pcontact)
		self.ewarn("| Distributed under the " + other.plicense)
		self.ewarn("---------------------------")

	# Creates a symlink in /boot that points back to itself
	def create_bootlink(self):
		if not os.path.exists("/boot/boot"):
			self.eprint("Toolkit", "Creating /boot symlink in /boot ...")

			os.chdir("/boot")
			os.symlink(".", "boot")

			if not os.path.exists("/boot/boot"):
				self.ewarn("[Toolkit] Error creating /boot symlink!")
			else:
				self.esucc("[Toolkit] Successfully created /boot symlink!")

	# Cleanly exit the application
	def die(self, message):
		call(["echo", "-e", "\e[1;31m[Toolkit] " + message + 
		      ". Exiting ...\e[0;m"])

		# Remove the incomplete bootloader file
		if conf.bootloader == "grub2":
			if os.path.exists("grub.cfg"):
				os.remove("grub.cfg")
		elif conf.bootloader == "extlinux":
			if os.path.exists("extlinux.conf"):
				os.remove("extlinux.conf")

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

	# Prints a message with the module name included
	def eprint(self, module, message):
		call(["echo", "-e", "\e[1;36m[" + module + "] " + message + "\e[0;m "])

	# Used for successful entries
	def esucc(self, x):
		call(["echo", "-e", "\e[1;32m" + x + "\e[0;m"])

	# Used for warnings
	def ewarn(self, x):
		call(["echo", "-e", "\e[1;33m" + x + "\e[0;m "])
