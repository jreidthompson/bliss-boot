# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

from subprocess import call
from subprocess import check_output

import libs.Variables as var

# Provides basic utilities that can be used by any class (Colorized printing, parameter retrieval, etc)
class Toolkit:
	args_force = 0
	args_output = ""
	bl_drive = ""
	bl_extlinux = 0
	bl_el_path = "/boot/extlinux"
	bl_grub2 = 0

	args_options = (
		("-o", "--output"),
		("-f", "--force"),
		("-d", "--drive"),
		("-E", "--install-extlinux"),
		("-G", "--install-grub2"),
		("-h", "--help"),
	)

	# Checks to see if a parameter is a valid flag
	@classmethod
	def is_flag(cls, candidate):
		for i in range(len(cls.args_options)):
			for j in range(len(cls.args_options[i])):
				if cls.args_options[i][j] == candidate:
						return 0

		return -1

	# Checks parameters and running user
	@classmethod
	def welcome(cls):
		user = check_output(["whoami"], universal_newlines=True).strip()

		if user != "root":
			cls.die("This program must be ran as root")

		arguments = sys.argv[1:]

		if len(arguments) >= 1:
			for i in range(len(arguments)):
				# Sets the output file to write the config to
				if arguments[i] == "-o" or arguments[i] == "--output":
					try:
						if cls.is_flag(arguments[i+1]) != 0:
							cls.args_output = arguments[i+1]
					except IndexError:
						cls.die("You need to pass a path to output the file!")

				# Set 'force' in order to overwrite output file target
				elif arguments[i] == "-f" or arguments[i] == "--force":
					cls.args_force = 1

				# Set the drive where we want to install the bootloader
				elif arguments[i] == "-d" or arguments[i] == "--drive":
					try:
						if cls.is_flag(arguments[i+1]) != 0:
							cls.bl_drive = arguments[i+1]
					except IndexError:
						pass

				# Let the program know that we want to install extlinux
				elif arguments[i] == "-E" or arguments[i] == "--install-extlinux":
					cls.bl_extlinux = 1

					try:
						if cls.is_flag(arguments[i+1]) != 0:
							cls.bl_el_path = arguments[i+1]
					except IndexError:
						pass

				# Let the program know that we want to install GRUB 2
				elif arguments[i] == "-G" or arguments[i] == "--install-grub2":
					cls.bl_grub2 = 1

				# Displays the help/usage message
				elif arguments[i] == "-h" or arguments[i] == "--help":
					cls.print_usage()

	# Prints the header information
	@classmethod
	def print_info(cls):
		cls.ewarn("---------------------------")
		cls.ewarn(var.name + " - v" + var.version)
		cls.ewarn(var.contact)
		cls.ewarn("Distributed under the " + var.license)
		cls.ewarn("---------------------------")
		print("")

	# Prints the usage information
	@staticmethod
	def print_usage():
		print("Usage: bliss-boot [OPTION]\n")
		print("-o, --output\t\t\tGenerates the configuration file at this location.\n")
		print("-f, --force\t\t\tOverwrites the file at the target output path.\n")
		print("-d, --drive\t\t\tSpecifies the target drive to install the bootloader at.\n")
		print("-E, --install-extlinux\t\tInstalls extlinux and the MBR to the target path on disk and /boot drive (in fstab).")
		print("\t\t\t\tExample: bliss-boot -E (optional: target folder) (optional: -d <drive>)\n")
		print("-G, --install-grub2\t\tInstalls grub 2 to your drive")
		print("\t\t\t\tExample: bliss-boot -G (optional: -d <drive>)\n")
		print("-h, --help\t\t\tPrints this help message and then exits.\n")
		quit(0)

	# Cleanly exit the application
	@classmethod
	def die(cls, message):
		call(["echo", "-e", cls.colorize("red", message)])
		quit(1)

	# Returns the string with a color to be used in bash
	@staticmethod
	def colorize(color, message):
		if color == "red":
			colored_message = "\e[1;31m" + message + "\e[0;m"
		elif color == "yellow":
			colored_message = "\e[1;33m" + message + "\e[0;m"
		elif color == "green":
			colored_message = "\e[1;32m" + message + "\e[0;m"
		elif color == "cyan":
			colored_message = "\e[1;36m" + message + "\e[0;m"
		elif color == "none":
			colored_message = message

		return colored_message

	# Prints a message
	@classmethod
	def eprint(cls, message):
		call(["echo", "-e", cls.colorize("cyan", message)])

	# Used for successful entries
	@classmethod
	def esucc(cls, message):
		call(["echo", "-e", cls.colorize("green", message)])

	# Used for warnings
	@classmethod
	def ewarn(cls, message):
		call(["echo", "-e", cls.colorize("yellow", message)])

	# Returns the value of whether or not GRUB 2 will be installed
	@classmethod
	def is_grub2(cls):
		return cls.bl_grub2

	# Returns the value of whether or not extlinux will be installed
	@classmethod
	def is_extlinux(cls):
		return cls.bl_extlinux

	# Returns a positive number if an output option was set
	@classmethod
	def is_output(cls):
		if cls.args_output:
			return 1

		return 0

	# Gets the desired output path
	@classmethod
	def get_output_file(cls):
		return cls.args_output

	# Returns the value of whether or not we will overwrite the output file if it exists.
	@classmethod
	def is_force(cls):
		return cls.args_force

	# Returns extlinux variables
	@classmethod
	def get_el_path(cls):
		return cls.bl_el_path

	# Sets the bootloader drive
	@classmethod
	def set_bl_drive(cls, drive):
		cls.bl_drive = drive

	# Returns the bootloader drive
	@classmethod
	def get_bl_drive(cls):
		return cls.bl_drive

