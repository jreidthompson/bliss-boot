# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from etc import conf

class Manager(object):
	def __init__(self):
		print("[Manager] Activated")

		# Kernel Names and Kernel Values
		self.__ck_names = []
		self.__ck_values = []

	# Sets the kernel set to be used
	def set_kernel_list(self, kernels):
		self.__kernels = kernels
		self.convert_to_list(self)
	
	def print_kernels(self):
		for i in self.__kernels:
			print("[Manager] Kernel: " + i)

	def write_entries(self):
		# Check to see what's the bootloader before we start adding
		# all the entries, depending the bootloader we can cleanly start
		# adding generic information like default kernel, timeouts, etc
		if conf.bootloader == "grub2":
			print("[Manager] Generating GRUB 2 configuration ...")

			# Open it in write mode (erase old file) to start from a
			# clean slate.
			dossier = open("grub.cfg", "w")
			dossier.write("set timeout=" + conf.timeout + "\n")
			dossier.write("set default=" + conf.default + "\n")
			dossier.write("\n")
			dossier.close()
		else:
			print("[Manager] No bootloader detected. Exiting ...")
			quit(2)

		for kernel in self.__kernels:
			# If the kernel is found then add the entry
			if kernel in conf.kernels.keys():
				print("[Manager] Entry Matched: " + kernel)

				# Depending the bootloader we have specified, generate
				# its appropriate configuration.
				if conf.bootloader == "grub2":
					print("[Manager] Generating GRUB 2 configuration")

					full_kernel_path = conf.bootdir + "/" + kernel

					# Open it in append mode since the header was previously
					# created before.
					dossier = open("grub.cfg", "a")
					dossier.write("menuentry \"Funtoo - " + kernel +
						"\" {\n")
					dossier.write("\tlinux " + full_kernel_path + "/vmlinuz " +
						conf.kernels[kernel] + "\n")
					dossier.write("\tinitrd " + full_kernel_path + "/initrd\n")
					dossier.write("}\n")
					dossier.close()
			else:
				print("[Manager] Entry options not in etc/conf.py: " + kernel)

	# Converts the dictionary into two separate lists so that we can perform
	# index operations (Example: set default=2)
	def convert_to_list(self):
		for x in conf.kernels.keys():
			self.__ck_names.append(x)

		for x in conf.kernels.values():
			self.__ck_values.append(x)

		for i in range(len(self.__ck_names)):
			print("Key: {}, Value: {}".format(self.__ck_names[i],
			                                  self.__ck_values[i]))
	
	# Returns the index for this kernel
	def search(self, target):
		print("Searching:")
		for i in range(len(self.__ck_names)):
			if self.__ck_names[i] == target:
				print("[Manager] " + target + " has been found at index " + i)
				return i

		return -1

"""
set timeout=1
set default=0

# Funtoo
menuentry "Funtoo - 3.12.9-KS.01" {
>   insmod part_gpt
>   insmod ext2

>   set root='(md/0)'

>   linux /vmlinuz-3.12.9-KS.01 root=/dev/vg/root options="ro" quiet
>   initrd /initrd
}
"""
