# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil

from libs.Toolkit import Toolkit as tools

from subprocess import call

class Installer:
	def __init__(self, drive):
		self.grub2 = tools.is_grub2()
		self.extlinux = tools.is_extlinux()
		self.bootloader = self.get_boot_install()
		self.drive = drive

		# Extlinux
		self.path = tools.get_el_path()
		self.drive_number = -1
		self.drive_type = "none"

	# Starts the bootloader install process
	def start(self):
		if self.bootloader == "grub2":
			self.install_grub2()
		elif self.bootloader == "extlinux":
			self.install_extlinux()
		else:
			tools.ewarn("Skipping bootloader installation ...")

	# Sets the drive's partition number (used for extlinux: example: /dev/sda1 = 1)
	def set_drive_number(self, number):
		self.drive_number = number

	# Gets the drive's partition number
	def get_drive_number(self):
		return self.drive_number
	
	# Sets the drive's partition layout (gpt, msdos, etc)
	def set_drive_type(self, drive_type):
		self.drive_type = drive_type

	# Gets the drive's partition layout
	def get_drive_type(self):
		return self.drive_type

	# Sets the bootloader we want to install
	def set_bootloader(self, bootloader):
		self.bootloader = bootloader

	# Gets the bootloader we want to install
	def get_bootloader(self):
		return self.bootloader

	# Returns the bootloader to install if any
	def get_boot_install(self):
		if self.grub2 == 1 and self.extlinux == 1:
			tools.die("You cannot install both extlinux and grub2 in the same run!")
		elif self.grub2 == 1:
			return "grub2"
		elif self.extlinux == 1:
			return "extlinux"

	# Installs GRUB 2
	def install_grub2(self):
		if self.drive:
			tools.eprint("Installing GRUB 2 to " + self.drive + " ...")

			try:
				result = call(["grub2-install", self.drive])

				if result == 0:
					tools.esucc("GRUB 2 Installed Successfully!")
				else:
					tools.die("Failed to install GRUB 2 into " + self.drive + " !")

			except FileNotFoundError:
				tools.die("GRUB 2 isn't installed. Please install it and try again!")
		else:
			tools.die("The GRUB 2 drive has not been defined!")

	# Installs Extlinux
	def install_extlinux(self):
		tools.eprint("Installing extlinux to " + self.path + " and writing firmware to " + self.drive + " ...")

		# First make the directory to install extlinux in
		if not os.path.exists(self.path):
			print("el dir doesnt exist.. creatng")
			os.makedirs(self.path)

			if not os.path.exists(self.path):
				tools.die("Unable to create the " + self.path + " directory ...")

			print("el dir created succ")

		# Install extlinux to folder
		try:
			result = call(["extlinux", "--install", self.path])
		except FileNotFoundError:
			tools.die("extlinux is not installed! Please install it and try again.")

		if result == 0:
			tools.esucc("Extlinux was installed successfully to " + self.path + "!")
		elif result != 0:
			tools.die("Failed to install extlinux into " + self.path)

		# Copy menu.c32 and libutil.c32
		el_files = [
			"/usr/share/syslinux/menu.c32",
			"/usr/share/syslinux/libutil.c32"
		]

		for i in el_files:
			if os.path.isfile(i):
				shutil.copy(i, self.path)

				if not os.path.isfile(self.path + "/" + os.path.basename(i)):
					tools.die("Failed to copy " + os.path.basename(i) + "!") 
			else:
				tools.die(os.path.basename(i) + " doesn't exist")

		# GPT
		if self.drive_type == "gpt":
			firm = "/usr/share/syslinux/gptmbr.bin"

			# Toggle GPT bios bootable flag
			cmd = "sgdisk " + self.drive + " --attributes=" + self.drive_number + ":set:2"
			result = call(cmd, shell=True)
			
			if result == 0:
				tools.esucc("Succesfully toggled legacy bios bootable flag!")
				cmd = "sgdisk " + self.drive + " --attributes=" + self.drive_number + ":show"

				try:
					result = call(cmd, shell=True)
				except FileNotfoundError:
					tools.die("gptfdisk is not installed! Please install it and try again.")

			elif result != 0:
				tools.die("Error setting legacy bios bootable flag!")
		# MBR
		elif self.drive_type == "msdos":
			firm = "/usr/share/syslinux/mbr.bin"

		# Write the firmware to the drive
		if self.drive_type == "gpt" or self.drive_type == "msdos":
			if os.path.isfile(firm):
				tools.eprint("Writing firmware to " + self.drive + " ...")

				cmd = "dd bs=440 conv=notrunc count=1 if=" + firm + " of=" + self.drive
				result = call(cmd, shell=True)

				if result == 0:
					tools.esucc(os.path.basename(firm) + " was successfully written to " + self.drive + "!")
				elif result != 0:
					tools.die("Failed to write extlinux firmware to " + self.drive + "!")
		else:
			tools.die("Unable to determine firmware to use for extlinux ...")
