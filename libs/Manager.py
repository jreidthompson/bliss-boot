# Copyright (C) 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from libs.Toolkit import Toolkit
from libs.Scanner import Scanner

tools = Toolkit()
scanner = Scanner()

conf = tools.get_conf()

class Manager(object):
	def __init__(self):
		# Find all kernels in /boot/kernels
		self.set_kernel_list(scanner.get_kernels())

		# Find all the kernels in etc/conf.py's 'kernels' variable
		self.get_conf_kernels()

		# Build a new list with the common kernels from both lists
		# Basically it's an AND operation on two lists, which we will use
		# to keep the bootloader entries and default kernel value in sync
		self.common_kernels = tools.find_common_kernels(self.kernels, self.ck_names)

		# Checks to see that at least one kernel entry will be written
		self.check_kernels()

	# Sets the kernel set to be used
	def set_kernel_list(self, kernels):
		self.kernels = kernels

	# Prints the kernels detected in etc/conf.py
	def print_kernels(self):
		tools.eprint("Kernels detected in configuration:")

		for i in range(len(self.ck_names)):
			tools.eprint(self.ck_names[i])
	
	# Checks to see if any kernels will be added to the configuration file
	def check_kernels(self):
		if not self.common_kernels:
			tools.die("Please add your desired kernels and their options to the 'kernels' list\n" + 
					  "in " + tools.get_conf_file() + ". These entries should match the kernels you\n" +
					  "have in " + conf.bootdir + ".")

	# Converts the etc/conf.py's kernels dictionary into two separate lists
	# so that we can perform index operations (Example: set default=2)
	def get_conf_kernels(self):
		self.ck_names = []
		self.ck_values = []

		for x in conf.kernels.keys():
			self.ck_names.append(x)

		for x in conf.kernels.values():
			self.ck_values.append(x)

	# Returns the index for this kernel in the common kernel list
	def search(self, target):
		for i in range(len(self.common_kernels)):
			if self.common_kernels[i] == target:
				return i

		return -1

	# Prints the kernels found in common
	def print_common_kernels(self):
		for k in range(len(self.common_kernels)):
			tools.eprint("Common: " + self.common_kernels[k])
	
	# Gets and sets the parameters retrieved from the parameters
	def set_args(self, atool):
		self.args_force = atool.get_args_force()
		self.args_output = atool.get_args_output()
		self.boot_install = atool.get_boot_install()
		self.args_el_path = atool.get_el_path()
	
	# Installs the bootloader
	def install_bootloader(self):
		# What bootloader are we going to install?
		bootl = self.boot_install

		# Run this so we can set the layout that we need (we dont need the return value atm)
		scanner.get_bootdrive()
		layout = scanner.get_layout()
		bootdr = scanner.get_bootd_root()
		bootdr_num = scanner.get_bootd_num()

		if bootl == 1:
			tools.install_grub2(bootdr)
		elif bootl == 2:
			if bootdr_num != -1:
				tools.install_extlinux(self.args_el_path, bootdr, bootdr_num, layout)
			else:
				tools.ewarn("Unable to get proper boot drive number for setting Legacy BIOS Bootable flag. Skipping bootloader installation ...")
		else:
			tools.ewarn("Skipping bootloader installation ...")

	def write_entries(self):
		# Set up the output file
		self.output_file = ""

		if self.args_output != -1:
			self.output_file = self.args_output
		elif self.args_output == -1 and conf.bootloader == "grub2": 
			self.output_file = "grub.cfg"
		elif self.args_output == -1 and conf.bootloader == "extlinux":
			self.output_file = "extlinux.conf"

		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		position = self.search(conf.default)

		if position != -1:
			if conf.bootloader == "grub2":
				tools.eprint("Generating GRUB 2 configuration ...")

				bootdrive = scanner.get_bootdrive()

				if os.path.exists(self.output_file):
					if self.args_force == 1:
						dossier = open(self.output_file, "w")
					else:
						tools.die("Target file: " + self.output_file + " already exists. Pass -f to overwrite.")
				else:
					dossier = open(self.output_file, "w")

				dossier.write("set timeout=" + str(conf.timeout) + "\n")
				dossier.write("set default=" + str(position) + "\n")
				dossier.write("\n")

				# Write the modules that need to be inserted depending
				# drive style. For whole disk zfs, none will be returned
				# since a person can partition the drive manually and use msdos,
				# or they can let zfs format their drive automatically with
				# gpt. This amgiguity will be the reason both grub modules will
				# be inserted.
				if scanner.get_layout() == "gpt":
					dossier.write("insmod part_gpt\n")
				elif scanner.get_layout() == "msdos":
					dossier.write("insmod part_msdos\n")
				elif scanner.get_layout() == "none" or not scanner.get_layout():
					dossier.write("insmod part_gpt\n")
					dossier.write("insmod part_msdos\n")

				if conf.efi == 1:
					dossier.write("insmod efi_gop\n")
					dossier.write("insmod efi_uga\n")
					dossier.write("insmod fat\n")

				if conf.zfs == 1:
					dossier.write("insmod zfs\n")

				if conf.goody_bag:
					for candy in conf.goody_bag:
						dossier.write("insmod " + candy + "\n")

				if conf.zfs == 0:
					dossier.write("\nset root='" + bootdrive + "'\n")

				dossier.write("\n")
				dossier.close()
			elif conf.bootloader == "extlinux":
				tools.eprint("Generating extlinux configuration ...")

				if os.path.exists(self.output_file):
					if self.args_force == 1:
						dossier = open(self.output_file, "w")
					else:
						tools.die("Target file: " + self.output_file + " already exists. Pass -f to overwrite.")
				else:
					dossier = open(self.output_file, "w")

				dossier.write("TIMEOUT " + str(int(conf.timeout * 10)) + "\n")

				if conf.el_auto_boot == 0:
					dossier.write("UI " + conf.el_ui + "\n")

				dossier.write("\n")
				dossier.write("DEFAULT Funtoo" + str(position) + "\n\n")
				dossier.write("MENU TITLE " + conf.el_m_title + "\n")
				dossier.write("MENU COLOR title " + conf.el_c_title + "\n")
				dossier.write("MENU COLOR border " + conf.el_c_border + "\n")
				dossier.write("MENU COLOR unsel " + conf.el_c_unsel + "\n")
				dossier.write("\n")
				dossier.close()
			else:
				tools.die("The bootloader defined in " + tools.get_conf_file() + " is not supported.")
		else:
			tools.die("The default kernel entry in " + tools.get_conf_file() + "\nwas not found in " + conf.bootdir)

		# Add all our desired kernels
		for kernel in self.kernels:
			position = self.search(kernel)

			if position != -1:
				tools.esucc("Adding: " + kernel)

				cs = tools.strip_head(conf.bootdir)
				full_kernel_path = cs + "/" + kernel

				# Depending the bootloader we have specified, generate
				# its appropriate configuration.
				if conf.bootloader == "grub2":
					# Open it in append mode since the header was previously
					# created before.
					dossier = open(self.output_file, "a")
					dossier.write("menuentry \"Funtoo - " + kernel + "\" {\n")

					if conf.zfs == 0:
						dossier.write("\tlinux " + full_kernel_path + "/vmlinuz " + conf.kernels[kernel] + "\n")

						if conf.initrd == 1:
							dossier.write("\tinitrd " + full_kernel_path + "/initrd\n")
					else:
						dossier.write("\tlinux " + bootdrive + "/@" + full_kernel_path + "/vmlinuz " + conf.kernels[kernel] + "\n")

						if conf.initrd == 1:
							dossier.write("\tinitrd " + bootdrive + "/@" + full_kernel_path + "/initrd\n")

					dossier.write("}\n\n")
					dossier.close()
				elif conf.bootloader == "extlinux":
					dossier = open(self.output_file, "a")
					dossier.write("LABEL Funtoo" + str(position) + "\n")
					dossier.write("\tMENU LABEL Funtoo " + kernel + "\n")
					dossier.write("\tLINUX " + full_kernel_path + "/vmlinuz" + "\n")

					if conf.initrd == 1:
						dossier.write("\tINITRD " + full_kernel_path +
						"/initrd\n")

					dossier.write("\tAPPEND " + conf.kernels[kernel] + "\n")
					dossier.write("\n")
					dossier.close()
			else:
				tools.ewarn("Skipping: " + kernel)

		# Append anything else the user wants automatically added
		if conf.append == 1 and conf.append_stuff:
			tools.eprint("Appending additional information ...")

			if conf.bootloader == "grub2":
				dossier = open(self.output_file, "a")
				dossier.write(conf.append_stuff)
				dossier.close()
			elif conf.bootloader == "extlinux":
				dossier = open(self.output_file, "a")
				dossier.write(conf.append_stuff)
				dossier.close()

		# Check to make sure that the file was created successfully.
		# If so let the user know..
		if os.path.isfile(self.output_file):
			tools.esucc("'" + self.output_file + "' has been created!")
		else:
			tools.die("Either the file couldn't be created or the specified\nbootloader isn't supported.")
