# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
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
		self.common_kernels = tools.find_common_kernels(
		                      self.kernels, self.ck_names)

		# Checks to see that at least one kernel entry will be written
		self.check_kernels()

	# Sets the kernel set to be used
	def set_kernel_list(self, kernels):
		self.kernels = kernels

	# Prints the kernels detected in etc/conf.py
	def print_kernels(self):
		tools.eprint("Manager", "Kernels detected in configuration:")

		for i in range(len(self.ck_names)):
			tools.eprint("Manager", self.ck_names[i])
	
	# Checks to see if any kernels will be added to the configuration file
	def check_kernels(self):
		if not self.common_kernels:
			tools.die("Make sure you have a kernel and corresponding config")

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
			tools.eprint("Manager", "Common: " + self.common_kernels[k])

	def write_entries(self):
		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		position = self.search(conf.default)

		if position != -1:
			if conf.bootloader == "grub2":
				tools.eprint("Manager", "Generating GRUB 2 configuration ...")

				bootdrive = scanner.get_bootdrive()

				# Open it in write mode (erase old file) to start from a
				# clean slate.
				dossier = open("grub.cfg", "w")
				dossier.write("set timeout=" + str(conf.timeout) + "\n")
				dossier.write("set default=" + str(position) + "\n")
				dossier.write("\n")

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
				tools.eprint("Manager", "Generating extlinux configuration ...")

				dossier = open("extlinux.conf", "w")
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
			elif conf.bootloader == "lilo":
				tools.eprint("Manager", "Generating lilo configuration ...")

				bootdrive = scanner.get_bootdrive()

				dossier = open("lilo.conf", "w")

				dossier.write("boot = " + bootdrive + "\n")
				dossier.write("timeout = " + str(int(conf.timeout * 10)) + "\n")
				dossier.write("default = " + conf.default  + "\n")

				if conf.lilo_bag:
					dossier.write("\n")
					for lo in conf.lilo_bag:
						dossier.write(lo + "\n")

				dossier.write("\n")
				dossier.close()
			else:
				tools.die("No bootloader defined in configuration")
		else:
			tools.die("Default boot entry not found in " + conf.bootdir)

		# Add all our desired kernels
		for kernel in self.kernels:
			position = self.search(kernel)

			if position != -1:
				tools.esucc("[Manager] Adding: " + kernel)

				full_kernel_path = conf.bootdir + "/" + kernel

				# Depending the bootloader we have specified, generate
				# its appropriate configuration.
				if conf.bootloader == "grub2":
					# Open it in append mode since the header was previously
					# created before.
					dossier = open("grub.cfg", "a")
					dossier.write("menuentry \"Funtoo - " + kernel +
							"\" {\n")

					if conf.zfs == 0:
						dossier.write("\tlinux " + full_kernel_path +
						"/vmlinuz " + conf.kernels[kernel] + "\n")

						if conf.initrd == 1:
							dossier.write("\tinitrd " + full_kernel_path +
							"/initrd\n")
					else:
						dossier.write("\tlinux " + bootdrive + "/@" +
						full_kernel_path + "/vmlinuz " + conf.kernels[kernel] +
						"\n")

						if conf.initrd == 1:
							dossier.write("\tinitrd " + bootdrive + "/@" +
							full_kernel_path + "/initrd\n")

					dossier.write("}\n\n")
					dossier.close()
				elif conf.bootloader == "extlinux":
					dossier = open("extlinux.conf", "a")
					dossier.write("LABEL Funtoo" + str(position) + "\n")
					dossier.write("\tMENU LABEL Funtoo " + kernel +
					"\n")
					dossier.write("\tLINUX " + full_kernel_path + "/vmlinuz" +
					"\n")

					if conf.initrd == 1:
						dossier.write("\tINITRD " + full_kernel_path +
						"/initrd\n")

					dossier.write("\tAPPEND " + conf.kernels[kernel] + "\n")
					dossier.write("\n")
					dossier.close()
				elif conf.bootloader == "lilo":
					dossier = open("lilo.conf", "a")

					dossier.write("image = " + full_kernel_path + "/vmlinuz\n")
					dossier.write("\tlabel = " + kernel + "\n")
					dossier.write("\tappend = '" + conf.kernels[kernel] +
					              "'\n")
					dossier.write("\tinitrd = " + full_kernel_path + 
					              "/initrd\n\n")
					dossier.close()
			else:
				tools.ewarn("[Manager] Skipping: " + kernel)

		# Append anything else the user wants automatically added
		if conf.append == 1 and conf.append_stuff:
			tools.eprint("Manager", "Appending additional information ...")

			if conf.bootloader == "grub2":
				dossier = open("grub.cfg", "a")
				dossier.write(conf.append_stuff)
				dossier.close()
			elif conf.bootloader == "extlinux":
				dossier = open("extlinux.conf", "a")
				dossier.write(conf.append_stuff)
				dossier.close()
			elif conf.bootloader == "lilo":
				dossier = open("lilo.conf", "a")
				dossier.write(conf.append_stuff)
				dossier.close()

		# Check to make sure that the file was created successfully.
		# If so let the user know..
		if conf.bootloader == "grub2" and os.path.isfile("grub.cfg"):
			tools.esucc("[Manager] 'grub.cfg' has been created!")
		elif conf.bootloader == "extlinux" and os.path.isfile("extlinux.conf"):
			tools.esucc("[Manager] 'extlinux.conf' has been created!")
		elif conf.bootloader == "lilo" and os.path.isfile("lilo.conf"):
			tools.esucc("[Manager] 'lilo.conf' has been created!")
			tools.esucc("[Manager] Please place this file in /etc/lilo.conf " +
			            "and run 'lilo -v'.")
		else:
			tools.die("Either the file couldn't be created or the " +
			"specified bootloader is unsupported.")
