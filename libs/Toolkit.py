# Copyright (C) 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
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

from importlib import machinery

from . import other

# Path to config file
config_loc = "/etc/bliss-boot/conf.py"

# Explictly load the conf file without using the 'get_conf' function
loader = machinery.SourceFileLoader("conf", config_loc)
conf = loader.load_module("conf")

class Toolkit(object):
	extlinux = -1
	grub2 = -1

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
						self.extlinux = 1

						# Path to where we want to install Extlinux
						self.args_el_path = arguments[i+1]
					except IndexError:
						self.die("You need to pass a path to install extlinux!\n" +
						         "Example: bliss-boot -E /boot/extlinux")

				# Let the program know that we want to install GRUB 2
				elif arguments[i] == "-G" or arguments[i] == "--install-grub2":
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
	
	# Installs GRUB 2
	def install_grub2(self, drive):
		self.eprint("Installing GRUB 2 to " + drive + " ...")

		result = call(["grub-install", drive])

		if result == 0:
			self.esucc("GRUB 2 Installed Successfully!")
		elif result != 0:
			self.die("Failed to install GRUB 2 into " + drive)

	# Installs Extlinux
	def install_extlinux(self, path, drive, dnum, mtype):
		self.eprint("Installing extlinux to " + path + " and writing firmware to " + drive + " ...")

		# First make the directory to install extlinux in
		if not os.path.exists(path):
			os.makedirs(path)

			if not os.path.exists(path):
				self.die("Unable to create the " + path + " directory ...")

		# Install extlinux to folder
		result = call(["extlinux", "--install", path])

		if result == 0:
			self.esucc("Extlinux was installed successfully to " + path + "!")
		elif result != 0:
			self.die("Failed to install extlinux into " + path)

		# Copy menu.c32 and libutil.c32
		el_files = [
			"/usr/share/syslinux/menu.c32",
			"/usr/share/syslinux/libutil.c32"
		]

		for i in el_files:
			if os.path.isfile(i):
				shutil.copy(i, path)

				if not os.path.isfile(path + "/" + os.path.basename(i)):
					self.die("Failed to copy " + os.path.basename(i) + "!") 
			else:
				self.die(os.path.basename(i) + " doesn't exist")

		# GPT
		if mtype == "gpt":
			firm = "/usr/share/syslinux/gptmbr.bin"

			# Toggle GPT bios bootable flag
			cmd = "sgdisk " + drive + " --attributes=" + dnum + ":set:2"
			result = call(cmd, shell=True)
			
			if result == 0:
				self.esucc("Succesfully toggled legacy bios bootable flag!")
				cmd = "sgdisk " + drive + " --attributes=" + dnum + ":show"
				result = call(cmd, shell=True)
			elif result != 0:
				self.die("Error setting legacy bios bootable flag!")
		# MBR
		elif mtype == "msdos":
			firm = "/usr/share/syslinux/mbr.bin"

		# Write the firmware to the drive
		if mtype == "gpt" or mtype == "msdos":
			if os.path.isfile(firm):
				self.eprint("Writing firmware to " + drive + " ...")

				cmd = "dd bs=440 conv=notrunc count=1 if=" + firm + " of=" + drive
				result = call(cmd, shell=True)

				if result == 0:
					self.esucc(os.path.basename(firm) + " was successfully written to " + drive + "!")
				elif result != 0:
					self.die("Failed to write extlinux firmware to " + drive + "!")
		else:
			self.die("Unable to determine firmware to use for extlinux ...")

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

	# Prints a message
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
