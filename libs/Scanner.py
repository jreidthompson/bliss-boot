# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import re

from libs.Toolkit import Toolkit
from libs.ConfigLoader import ConfigLoader

from subprocess import call
from subprocess import check_output

tools = Toolkit()
config = ConfigLoader.get_config()

class Scanner:
	def __init__(self):
		self.boot_kernels = []
		self.fstab_vals = []
		self.layout = ""

		# Kernels defined by user in configuration file (Example: Gentoo, 3.12.4-KS.01, root=/dev/sda1)
		self.ck_prefix = []
		self.ck_version = []
		self.ck_options = []

		# Factorized Kernels List (The kernels that were found in the bootdir and defined by user in the config)
		self.common_kernels = []

		# Get the fstab values for /boot immediately
		self.scan_fstab()

		# Detect the layout of the /boot drive
		self.detect_layout()

	# Finds the kernels that the user has in their 'config.bootdir' directory
	def find_boot_kernels(self):
		tools.eprint("Scanning " + config.bootdir + " ...") 

		# Check to see if our boot directory exists before starting
		if not os.path.exists(config.bootdir):
			tools.eprint("The " + config.bootdir + " directory doesn't exist. Creating ...")

			os.mkdir(config.bootdir)

			if os.path.exists(config.bootdir):
				tools.ewarn("Please place your kernels inside " + config.bootdir + "/<version>, configure " + ConfigLoader.get_config_file() + 
				            ", and then re-run the program. \n\nExample:\n\n" + config.bootdir + "/3.12.12-KS.01/{vmlinuz, initrd}")
				quit(0)
			else:
				tools.die(config.bootdir + " directory doesn't exist")

		cmd = 'ls ' + config.bootdir
		results = check_output(["ls", config.bootdir], universal_newlines=True).strip()
		
		# Add kernels to out kernel set
		if results:
			for i in results.split("\n"):
				self.boot_kernels.append(i)
		else:
			tools.die("No kernels found in " + config.bootdir + ". A directory for each kernel you want must exist " +
					  "in that location.\n\nExample:\n\n" + config.bootdir + "/3.13.5-KS.01/\n" + config.bootdir + "/3.14.1-KS.01/\n")

	# Get fstab information. We will use this to get /boot
	def scan_fstab(self):
		cmd = 'cat /etc/fstab | grep /boot[[:blank:]] | awk \'{print $1, $2, $3, $4, $5, $6}\''
		results = check_output(cmd, shell=True, universal_newlines=True).strip()

		if results:
			# Split the /boot line so we can store it
			splits = results.split(" ")

			# Save fstab /boot drive info
			for x in splits:
				self.fstab_vals.append(x.strip())
		else:
			tools.die("/boot line could not be found in /etc/fstab")

	# Detect the partition style for the /boot drive (gpt or mbr)
	# and returns either "gpt" or "msdos" as a string
	def detect_layout(self):
		# If we are using 'whole disk zfs', we know for a fact that
		# it's gpt (assuming the drive was formatted with zpool create).

		# However, if the person partitioned the drive manually and is
		# still using the whole drive for zfs (technically speaking),
		# then they could be using mbr as well.. returning 'none' so that
		# both part_<> can be included
		if config.zfs == 1:
			self.layout = "none"
		else:
			drive = self.fstab_vals[0]

			# Remove the partition number so that we can find the
			# style of the drive itself
			match = re.sub("\d$", "", drive)

			if match:
				# use blkid /dev/<drive> and get PTTYPE
				# example: blkid /dev/vda: -> /dev/vda: PTTYPE="gpt"
				cmd = 'blkid ' + match.strip() + ' | cut -d \'"\' -f 4'
				results = check_output(cmd, shell=True, universal_newlines=True).strip()

				if results:
					if results.strip() == "gpt":
						self.layout = "gpt"
					elif results.strip() == "dos":
						self.layout = "msdos"
					else:
						self.layout = "none"
				else:
					# This will run if we get some weird result like "md" from "/dev/md0"
					self.layout = "none"
			else:
				# If the layout couldn't be detected then return none so that both msdos/gpt can be inserted.
				# This will happen if the user has a raid or lvm device as their /boot.
				self.layout = "none"
	
	# Returns only the number of the boot drive
	def get_bootdrive_num(self):
		drive = self.fstab_vals[0]

		# This is the partition number which will be used to set the
		# Legacy BIOS Bootable flag if the user uses extlinux and it's GPT
		part_num = re.search("\d+", drive)

		if part_num:
			return part_num.group()
		else:
			tools.ewarn("Skipping extlinux bootloader installation since your /boot (" + drive + ") is probably on LVM.")
			return -1

	# Returns the drive root (i.e /dev/sda)
	def get_bootdrive(self):
		drive = self.fstab_vals[0]

		# Remove the partition number so that we can find the drive root
		match = re.sub("\d$", "", drive)

		if match:
			return match
		else:
			return -1

	# Converts the fstab /boot drive entry to a grub 2 compatible format
	# and returns it as a string: (gpt) /dev/sda1 -> (hd0,gpt1)
	def get_grub2_bootdrive(self):
		"""
		# If the person wants to use GRUB 2, and we can't detect the layout,
		# then there is no point in continuing since the set root will be incorrect.
		if self.layout == "none":
			tools.die("Unable to detect the partition layout for the /boot drive. GRUB 2 might not support it!\n" +
			          "If you are sure that GRUB 2 supports this drive layout, and you double checked everything\n" +
					  "Please submit a bug report with the contents of the following:\n\n" +

					  "- Contents of your 'bootdir'\n" +
					  "- Contents of /etc/bliss-boot/conf.py\n" +
					  "- Contents of /etc/fstab)\n" +
					  "- The result of 'blkid <your /boot drive from fstab>'")
		"""

		# If we are using 'whole disk zfs', then we won't have a /boot entry
		# in /etc/fstab. So instead we will format the zfs_boot variable and
		# return it ready to be used in grub2
		if config.zfs == 1:
			match = re.search('(/[a-zA-Z0-9_/]+)', config.zfs_boot)

			if match:
				return match.group()

			tools.die("Could not parse the 'zfs_boot' variable correctly.")

		if self.fstab_vals:
			drive = self.fstab_vals[0]

			match = re.search('/dev/(.*)', drive)

			if match:
				# Possibilities:
				# sd[a-z][0+]
				# vd[a-z][0+]
				# md[0+]
				# mapper/vg-root
				# vg/root

				# --- Handle sdX or vdX drives ---
				m1 = re.search('[s|v]d(\w+)', match.group(1))

				if m1:
					# Complete value, will be completed as function
					# progresses
					cval = "(hd"

					# Process the letter part and convert it to a grub
					# compatible format; a = (hd0)
					alph = re.search('\w', m1.group(1))

					if alph:
						# Find the number in the alphabet of this letter
						alphindex = tools.get_alph_index(alph.group(0))

						# Add this number to the final string
						cval = cval + str(alphindex)

					# Process the number part of the drive
					nump = re.search('\d', m1.group(1))

					if nump:
						# add layout
						cval = cval + "," + self.layout

						# add number part
						cval = cval + nump.group(0)

					# close the value and return it
					cval = cval + ")"

					return cval

				# --- Handle md# ---
				m1 = re.search('md(\d+)', match.group(1))

				if m1:
					return "(md/" + m1.group(1) + ")"

				# --- LVM: mapper/<volume_group>-<logical_volume> ---
				m1 = re.search('mapper/(\w.-\w+)', match.group(1))

				if m1:
					return "(lvm/" + m1.group(1) + ")"

				# --- LVM: <volume_group>/<logical_volume> ---
				m1 = re.search('(\w+)/(\w+)', match.group(1))

				if m1:
					return "(lvm/" + m1.group(1) + "-" + m1.group(2) + ")"

				# We've failed :(
				tools.die("Unable to generate the boot drive entry.")

	# Returns the kernel set that was gathered
	def get_boot_kernels(self):
		return self.boot_kernels

	# Prints a list of detected kernels in the boot directory
	def print_boot_kernels(self):
		tools.eprint("Kernels detected in the " + config.bootdir + " directory:")

		for i in self.boot_kernels:
			tools.eprint(i)

	# Finds the kernels that the user defined in their configuration file
	def find_config_kernels(self):
		tools.eprint("Scanning " + ConfigLoader.get_config_file() + " ...") 

		for x in config.kernels:
			self.ck_prefix.append(x[0])
			self.ck_version.append(x[1])
			self.ck_options.append(x[2])

	# Prints the kernels detected in the configuration file
	def print_config_kernels(self):
		tools.eprint("Kernels detected in " + ConfigLoader.get_config_file() + ":")

		for i in range(len(self.ck_prefix)):
			print(str(i+1) + ". " + self.ck_prefix[i] + " - " + self.ck_version[i])

	# Factors out the kernels that were defined by the user and found in their bootdir
	def factor_common_kernels(self):
		self.common_kernels = self.find_common_kernels(self.boot_kernels, self.ck_version)

	# Find values in common from two lists and return a third list
	def find_common_kernels(self, list_a, list_b):
		common_list = []

		for i in range(len(list_a)):
			for j in range(len(list_b)):
				if list_a[i] == list_b[j]:
					value = [ self.ck_prefix[j], self.ck_version[j], self.ck_options[j] ]
					common_list.append(value)

		return common_list

	# Gets the common kernel list
	def get_common_kernels(self):
		return self.common_kernels

	# Prints the kernels found in common
	def print_common_kernels(self):
		tools.eprint("Common kernels detected:")

		for k in range(len(self.common_kernels)):
			print(str(k+1) + ". " + self.common_kernels[k][0] + " - " + self.common_kernels[k][1])

	# Returns the index for target kernel in the common kernel list
	def search(self, target):
		for i in range(len(self.common_kernels)):
			if self.common_kernels[i][1] == target:
				return i

		return -1
	
	# Retrieves the kernel from the common list
	def get_kernel(self, target):
		return self.common_kernels[target]

	# Checks to see if any kernels will be added to the configuration file
	def any_kernels(self):
		if not self.common_kernels:
			return -1
		else:
			return 0

	# Gets the layout that was detected
	def get_layout(self):
		return self.layout
