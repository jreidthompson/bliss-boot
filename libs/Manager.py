# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from libs.Toolkit import Toolkit as tools
from libs.Scanner import Scanner
from libs.Installer import Installer
from libs.ConfigLoader import ConfigLoader

scanner = Scanner()

config = ConfigLoader.get_config()

class Manager:
	def __init__(self):
		# Find all the kernels in the user's boot directory (config.bootdir)
		scanner.find_boot_kernels()

		# Find all the kernels that the user configured in their configuration file
		scanner.find_config_kernels()

		# Find all the kernels that were found in their boot directory and where a definition was found in their configuration file
		scanner.factor_common_kernels()

		# Checks to see that at least one kernel entry will be written
		result = scanner.any_kernels()

		if result == -1:
			tools.die("Please add your desired kernels and their options to the 'kernels' list in " + ConfigLoader.get_config_file() + ".\n" +
			          "These entries should match the kernels you have in " + config.bootdir + ".")

		# Get /boot drive layout
		self.layout = scanner.get_layout()

	# Generates the bootloader configuration
	def write_entries(self):
		self.output_file = ""

		is_output = tools.is_output()

		if is_output:
			self.output_file = tools.get_output_file()
		elif not is_output and config.bootloader == "grub2": 
			self.output_file = "grub.cfg"
		elif not is_output and config.bootloader == "extlinux":
			self.output_file = "extlinux.conf"

		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		position = scanner.search(config.default)

		if position != -1:
			if config.bootloader == "grub2":
				tools.eprint("Generating GRUB 2 configuration ...")

				bootdrive = scanner.get_grub2_bootdrive()

				if os.path.exists(self.output_file):
					if tools.is_force():
						dossier = open(self.output_file, "w")
					else:
						tools.die("Target file: " + self.output_file + " already exists. Pass -f to overwrite.")
				else:
					dossier = open(self.output_file, "w")

				dossier.write("set timeout=" + str(config.timeout) + "\n")
				dossier.write("set default=" + str(position) + "\n")
				dossier.write("\n")

				# Write the modules that need to be inserted depending
				# drive style. For whole disk zfs, none will be returned
				# since a person can partition the drive manually and use msdos,
				# or they can let zfs format their drive automatically with
				# gpt. This amgiguity will be the reason both grub modules will
				# be inserted.

				if self.layout == "gpt":
					dossier.write("insmod part_gpt\n")
				elif self.layout == "msdos":
					dossier.write("insmod part_msdos\n")
				elif self.layout == "none":
					dossier.write("insmod part_gpt\n")
					dossier.write("insmod part_msdos\n")

				if config.efi == 1:
					dossier.write("insmod efi_gop\n")
					dossier.write("insmod efi_uga\n")
					dossier.write("insmod fat\n")

				if config.zfs == 1:
					dossier.write("insmod zfs\n")

				if config.goody_bag:
					for candy in config.goody_bag:
						dossier.write("insmod " + candy + "\n")

				if config.zfs == 0:
					dossier.write("\nset root='" + bootdrive + "'\n")

				dossier.write("\n")
				dossier.close()
			elif config.bootloader == "extlinux":
				tools.eprint("Generating extlinux configuration ...")

				dk_name = scanner.get_kernel(position)[0]

				if os.path.exists(self.output_file):
					if tools.is_force():
						dossier = open(self.output_file, "w")
					else:
						tools.die("Target file: " + self.output_file + " already exists. Pass -f to overwrite.")
				else:
					dossier = open(self.output_file, "w")

				dossier.write("TIMEOUT " + str(int(config.timeout * 10)) + "\n")

				if config.el_auto_boot == 0:
					dossier.write("UI " + config.el_ui + "\n")

				dossier.write("\n")
				dossier.write("DEFAULT " + dk_name + str(position) + "\n\n")
				dossier.write("MENU TITLE " + config.el_m_title + "\n")
				dossier.write("MENU COLOR title " + config.el_c_title + "\n")
				dossier.write("MENU COLOR border " + config.el_c_border + "\n")
				dossier.write("MENU COLOR unsel " + config.el_c_unsel + "\n")
				dossier.write("\n")
				dossier.close()
			else:
				tools.die("The bootloader defined in " + ConfigLoader.get_config_file() + " is not supported.")
		else:
			tools.die("The default kernel entry in " + ConfigLoader.get_config_file() + " was not found in " + config.bootdir)

		# Add all our desired kernels
		for kernel in scanner.get_common_kernels():
			position = scanner.search(kernel[1])

			if position != -1:
				tools.esucc("Adding: " + kernel[0] + " - " + kernel[1])

				cs = tools.strip_head(config.bootdir)
				full_kernel_path = cs + "/" + kernel[1]

				# Depending the bootloader we have specified, generate
				# its appropriate configuration.
				if config.bootloader == "grub2":
					# Open it in append mode since the header was previously
					# created before.
					dossier = open(self.output_file, "a")
					dossier.write("menuentry \"" + kernel[0] + " - " + kernel[1] + "\" {\n")

					if config.zfs == 0:
						dossier.write("\tlinux " + full_kernel_path + "/vmlinuz " + kernel[2] + "\n")

						if config.initrd == 1:
							dossier.write("\tinitrd " + full_kernel_path + "/initrd\n")
					else:
						dossier.write("\tlinux " + bootdrive + "/@" + full_kernel_path + "/vmlinuz " + kernel[2] + "\n")

						if config.initrd == 1:
							dossier.write("\tinitrd " + bootdrive + "/@" + full_kernel_path + "/initrd\n")

					dossier.write("}\n\n")
					dossier.close()
				elif config.bootloader == "extlinux":
					dossier = open(self.output_file, "a")
					dossier.write("LABEL " + kernel[0] + str(position) + "\n")
					dossier.write("\tMENU LABEL " + kernel[0] + " - " + kernel[1] + "\n")
					dossier.write("\tLINUX " + full_kernel_path + "/vmlinuz" + "\n")

					if config.initrd == 1:
						dossier.write("\tINITRD " + full_kernel_path + "/initrd\n")

					dossier.write("\tAPPEND " + kernel[2] + "\n")
					dossier.write("\n")
					dossier.close()

		# Append anything else the user wants automatically added
		if config.append == 1 and config.append_stuff:
			tools.eprint("Appending additional information ...")

			if config.bootloader == "grub2":
				dossier = open(self.output_file, "a")
				dossier.write(config.append_stuff)
				dossier.close()
			elif config.bootloader == "extlinux":
				dossier = open(self.output_file, "a")
				dossier.write(config.append_stuff)
				dossier.close()

		# Check to make sure that the file was created successfully.
		# If so let the user know..
		if os.path.isfile(self.output_file):
			tools.esucc("'" + self.output_file + "' has been created!")
		else:
			tools.die("Either the file couldn't be created or the specified\nbootloader isn't supported.")

	# Triggers bootloader installation
	def install_bootloader(self):
		# Set the drive using the /boot entry in /etc/fstab if the user wants 
		# to install a bootloader but didn't specify the drive themselves as an argument.
		if not tools.get_bl_drive():
			installer = Installer(scanner.get_bootdrive())
		else:
			installer = Installer(tools.get_bl_drive())

		# Set extlinux specific information before we start
		if installer.get_bootloader() == "extlinux":
			installer.set_drive_number(scanner.get_bootdrive_num())
			installer.set_drive_type(scanner.get_layout())

		installer.start()
