# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import shutil
import string

from subprocess import call
from subprocess import check_output

from . import other

class Toolkit(object):
	extlinux = -1
	grub2 = -1
	install_bl_flag = 0

	# Checks parameters and running user
	def welcome(self):
		arguments = sys.argv[1:]

		if len(arguments) >= 1:
			for i in range(len(arguments)):

				# Sets the output file to write the config to
				if arguments[i] == "-o" or arguments[i] == "--output":
					try:
						self.args_output = arguments[i+1]
					except IndexError:
						self.die("You need to pass a path to output the file!")

				# Set 'force' in order to overwrite output file target
				elif arguments[i] == "-f" or arguments[i] == "--force":
					self.args_force = 1

				# Let the program know that we want to install extlinux
				elif arguments[i] == "-E" or arguments[i] == "--install-extlinux":
					try:
						self.install_bl_flag = 1
						self.extlinux = 1

						# Path to where we want to install Extlinux
						self.args_el_path = arguments[i+1]
					except IndexError:
						self.die("You need to pass a path to install extlinux!\n" +
						         "Example: bliss-boot -E /boot/extlinux")

				# Let the program know that we want to install GRUB 2
				elif arguments[i] == "-G" or arguments[i] == "--install-grub2":
					self.install_bl_flag = 1
					self.grub2 = 1

				# Displays the help/usage message
				elif arguments[i] == "-h" or arguments[i] == "--help":
					self.print_usage()

		user = check_output(["whoami"], universal_newlines=True).strip()

		if user != "root":
			self.die("This program must be ran as root")

	def print_info(self):
		self.ewarn("---------------------------")
		self.ewarn("| " + other.pname + " - v" + other.pversion)
		self.ewarn("| Author: " + other.pcontact)
		self.ewarn("| Distributed under the " + other.plicense)
		self.ewarn("---------------------------")

	def print_usage(self):
		print("Usage: bliss-boot [OPTION]\n")
		print("-o, --output\t\t\tGenerates the configuration file at this location.\n")
		print("-f, --force\t\t\tOverwrites the file at the target output path.\n")
		print("-E, --install-extlinux\t\tInstalls extlinux and the MBR to the target path on disk and /boot drive (in fstab).")
		print("\t\t\t\tExample: bliss-boot -E /boot/extlinux\n")
		print("-G, --install-grub2\t\tInstalls grub 2 to your /boot drive (in fstab).")
		print("\t\t\t\tExample: bliss-boot -G\n")
		print("-h, --help\t\t\tPrints this help message and then exits.\n")
		quit(0)

	# Cleanly exit the application
	def die(self, message):
		call(["echo", "-e", "\e[1;31m" + message + "\e[0;m"])
		quit(5)
	
	# Get the index for a letter in the alphabet
	def get_alph_index(self, letter):
		alphabet = string.ascii_lowercase

		count = 0

		for let in alphabet:
			if let == letter:
				return count

			count = count + 1

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

	# Prints a message
	def eprint(self, x):
		call(["echo", "-e", "\e[1;36m" + x + "\e[0;m "])

	# Used for successful entries
	def esucc(self, x):
		call(["echo", "-e", "\e[1;32m" + x + "\e[0;m"])

	# Used for warnings
	def ewarn(self, x):
		call(["echo", "-e", "\e[1;33m" + x + "\e[0;m "])

	# Gets desired output path
	def get_args_output(self):
		try:
			return self.args_output
		except AttributeError:
			return -1

	# Returns if "force" is enabled for output file target
	def get_args_force(self):
		try:
			return self.args_force
		except AttributeError:
			return 0

	# Returns extlinux variables
	def get_el_path(self):
		try:
			return self.args_el_path
		except AttributeError:
			return 0

	# Returns the bootloader to install if any
	def get_boot_install(self):
		if self.grub2 == 1 and self.extlinux == 1:
			self.die("You cannot install both extlinux and grub2 in the same run!")
		elif self.grub2 == 1:
			return 1
		elif self.extlinux == 1:
			return 2
