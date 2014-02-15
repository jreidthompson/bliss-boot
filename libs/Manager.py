# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from libs import Toolkit
from libs import Scanner

from etc import conf

class Manager(object):
	def __init__(self):
		# Kernel Names and Kernel Values
		self.__ck_names = []
		self.__ck_values = []
		self.toolkit = Toolkit.Toolkit()
		self.scanner = Scanner.Scanner()

	# Sets the kernel set to be used
	def set_kernel_list(self, kernels):
		self.__kernels = kernels

		# Convert the dictionary into two lists. This will let us
		# search them by indexes.
		self.convert_to_list()
	
	def print_kernels(self):
		print("[Manager] Kernels detected in configuration:")
		for i in range(len(self.__ck_names)):
			print("[Manager] " + self.__ck_names[i])
	
	# Checks to see if any kernels will be added to the configuration file
	def check_kernels(self):
		for i in self.__kernels:
			if i in self.__ck_names:
				return 0
		
		self.toolkit.die("Make sure you have a kernel and corresponding config")

	def write_entries(self):
		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		if conf.bootloader == "grub2":
			print("[Manager] Generating GRUB 2 configuration ...")

			position = self.search(conf.default)

			if position != -1:
				# Open it in write mode (erase old file) to start from a
				# clean slate.
				dossier = open("grub.cfg", "w")
				dossier.write("set timeout=" + conf.timeout + "\n")
				dossier.write("set default=" + str(position) + "\n")
				dossier.write("\n")

				# Explicitly load gpt/msdos, modules, and boot drive until
				# better detection is implemented. I've noticed that even if
				# these modules aren't explictly loaded, GRUB 2 still works.
				dossier.write("insmod part_msdos\n")
				dossier.write("insmod part_gpt\n")

				if conf.efi == 1:
					dossier.write("insmod efi_gop\n")
					dossier.write("insmod efi_uga\n")
					dossier.write("insmod fat\n")

				dossier.write("\n")
				dossier.close()
			else:
				self.toolkit.die("Default boot entry not found")
		else:
			self.toolkit.die("No bootloader defined in configuration")

		for kernel in self.__kernels:
			# If the kernel is found then add the entry
			position = self.search(kernel)

			if position != -1:
				# Depending the bootloader we have specified, generate
				# its appropriate configuration.
				if conf.bootloader == "grub2":
					print("[Manager] Adding entry for " + kernel)

					full_kernel_path = conf.bootdir + "/" + kernel

					# Open it in append mode since the header was previously
					# created before.
					dossier = open("grub.cfg", "a")
					dossier.write("menuentry \"Funtoo - " + kernel +
						"\" {\n")

					# If 'bootdrive' isn't set, try to autodetect
					# using the /boot entry in /etc/fstab
					if not conf.bootdrive:
						bootdrive = self.scanner.get_bootdrive()
						dossier.write("\tset root='" + bootdrive + "'\n")
					else:
						dossier.write("\tset root='" + conf.bootdrive + "'\n")

					dossier.write("\n")
					dossier.write("\tlinux " + full_kernel_path + "/vmlinuz " +
						conf.kernels[kernel] + "\n")
					dossier.write("\tinitrd " + full_kernel_path + "/initrd\n")
					dossier.write("}\n\n")
					dossier.close()
			else:
				print("[Manager] Skipping " + kernel + " since it has been " + 
				"found in " + conf.bootdir + " but has not been defined " +
				"in conf.py")

	# Converts the dictionary into two separate lists so that we can perform
	# index operations (Example: set default=2)
	def convert_to_list(self):
		for x in conf.kernels.keys():
			self.__ck_names.append(x)

		for x in conf.kernels.values():
			self.__ck_values.append(x)

	# Returns the index for this kernel
	def search(self, target):
		for i in range(len(self.__ck_names)):
			if self.__ck_names[i] == target:
				return i

		return -1
