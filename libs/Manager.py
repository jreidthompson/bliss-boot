# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from libs.Toolkit import Toolkit
from libs.Scanner import Scanner

from etc import conf

toolkit = Toolkit()
scanner = Scanner()

class Manager(object):
	def __init__(self):
		# Kernel Names and Kernel Values
		self.ck_names = []
		self.ck_values = []

		# Find all kernels in /boot/kernels
		self.set_kernel_list(scanner.get_kernels())

		# Find all the kernels in etc/conf.py's 'kernels' variable
		self.get_conf_kernels()

		# Build a new list with the common kernels from both lists
		# Basically it's an AND operation on two lists, which we will use
		# to keep the bootloader entries and default kernel value in sync
		self.common_kernels = toolkit.find_common_kernels(
		                      self.kernels, self.ck_names)

		# Checks to see that at least one kernel entry will be written
		self.check_kernels()

	# Sets the kernel set to be used
	def set_kernel_list(self, kernels):
		self.kernels = kernels

	# Prints the kernels detected
	def print_kernels(self):
		print("[Manager] Kernels detected in configuration:")

		for i in range(len(self.ck_names)):
			print("[Manager] " + self.ck_names[i])
	
	# Checks to see if any kernels will be added to the configuration file
	def check_kernels(self):
		if not self.common_kernels:
			toolkit.die("Make sure you have a kernel and corresponding config")

		"""for i in self.kernels:
			if i in self.ck_names:
				return 0
		
		toolkit.die("Make sure you have a kernel and corresponding config")
		"""

	# Converts the etc/conf.py's kernels dictionary into two separate lists
	# so that we can perform index operations (Example: set default=2)
	def get_conf_kernels(self):
		for x in conf.kernels.keys():
			self.ck_names.append(x)

		for x in conf.kernels.values():
			self.ck_values.append(x)

	# Returns the index for this kernel in the /boot/kernels list
	def search(self, target):
		for i in range(len(self.kernels)):
			if self.kernels[i] == target:
				return i

		return -1

	# Returns the index for this kernel in the common kernel list
	def search_common(self, target):
		for i in range(len(self.common_kernels)):
			if self.common_kernels[i] == target:
				return i

		return -1

	# Returns the index for this kernel in the etc/conf.py's list
	def search_ck(self, target):
		print("Searching CK: " + target)
		for i in range(len(self.ck_names)):
			if self.ck_names[i] == target:
				print("Found CK: " + str(i))
				return i

		print("Not found CK: " + target)

		return -1

	def write_entries(self):
		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		position = self.search_common(conf.default)

		if position != -1:
			if conf.bootloader == "grub2":
				print("[Manager] Generating GRUB 2 configuration ...")

				bootdrive = scanner.get_bootdrive()

				# Open it in write mode (erase old file) to start from a
				# clean slate.
				dossier = open("grub.cfg", "w")
				dossier.write("set timeout=" + str(conf.timeout) + "\n")
				dossier.write("set default=" + str(position) + "\n")
				dossier.write("\n")

				# Add modules to load (depending machine layout)
				layout = scanner.get_layout()

				if layout == "gpt": 
					dossier.write("insmod part_gpt\n")
				elif layout == "msdos":
					dossier.write("insmod part_msdos\n")
				elif layout == "none":
					dossier.write("insmod part_gpt\n")
					dossier.write("insmod part_msdos\n")

				if scanner.lvm_status() == 1:
					dossier.write("insmod lvm\n")

				if conf.zfs == 1:
					dossier.write("insmod zfs\n")

				if conf.efi == 1:
					dossier.write("insmod efi_gop\n")
					dossier.write("insmod efi_uga\n")
					dossier.write("insmod fat\n")

				if conf.zfs == 0:
					dossier.write("\nset root='" + bootdrive + "'\n")

				dossier.write("\n")
				dossier.close()
			elif conf.bootloader == "extlinux":
				print("[Manager] Generating extlinux configuration ...")

				dossier = open("extlinux.conf", "w")
				dossier.write("TIMEOUT " + str(int(conf.timeout * 10)) + "\n")
				dossier.write("UI " + conf.el_ui + "\n")
				dossier.write("\n")
				dossier.write("MENU TITLE " + conf.el_m_title + "\n")
				dossier.write("MENU COLOR title " + conf.el_c_title + "\n")
				dossier.write("MENU COLOR border " + conf.el_c_border + "\n")
				dossier.write("MENU COLOR unsel " + conf.el_c_unsel + "\n")
				dossier.write("\n")
				dossier.close()
			else:
				toolkit.die("No bootloader defined in configuration")
		else:
			toolkit.die("Default boot entry not found in " + conf.bootdir)

		# For every kernel in /boot/kernels, search etc/conf.py before adding
		# and then add what needs to be added..
		for kernel in self.kernels:
			position = self.search_common(kernel)

			if position != -1:
				print("[Manager] ADDING: " + kernel)

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
			else:
				print("[Manager] SKIPPING: " + kernel + ". Found in " +
				conf.bootdir + " but not in etc/conf.py.")

		# Append anything else the user wants automatically added
		if conf.append == 1 and conf.append_stuff:
			if conf.bootloader == "grub2":
				dossier = open("grub.cfg", "a")
				dossier.write(conf.append_stuff)
				dossier.close()
			elif conf.bootloader == "extlinux":
				dossier = open("extlinux.conf", "a")
				dossier.write(conf.append_stuff)
				dossier.close()

		# Check to make sure that the file was created successfully.
		# If so let the user know..
		if conf.bootloader == "grub2" and os.path.isfile("grub.cfg"):
			print("[Manager] 'grub.cfg' has been created!")
		elif conf.bootloader == "extlinux" and os.path.isfile("extlinux.conf"):
			print("[Manager] 'extlinux.conf' has been created!")
		else:
			toolkit.die("Either the file couldn't be created or the " +
			"specified bootloader is unsupported.")

	# Prints the kernels found in common
	def print_common_kernels(self):
		for k in range(len(self.common_kernels)):
			print("Common: " + self.common_kernels[k])
