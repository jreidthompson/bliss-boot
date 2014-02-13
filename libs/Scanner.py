# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import re

from libs import Toolkit
from etc import conf

class Scanner(object):
	__kernels = set()
	__fstab_vals = []
	
	def __init__(self):
		self.toolkit = Toolkit.Toolkit()

	def find_kernels(self):
		print("[Scanner] Scanning: " + conf.bootdir) 

		# Check to see if our boot directory exists before starting
		if not os.path.exists(conf.bootdir):
			self.toolkit.die("Kernel boot directory doesn't exist")

		results = subprocess.Popen(
		          ["ls", conf.bootdir],
				  stdout=subprocess.PIPE,
		          universal_newlines=True)
		
		out = results.stdout.readlines()

		# Add kernels to out kernel set
		if out:
			for i in out:
				self.__kernels.add(i.strip())
		else:
			self.toolkit.die("No kernels in boot directory")
	
	# Detect the partition style (gpt or mbr)
	def detect_layout(self, options):
		print("[Scanner] Detecting Partition Layout ...")
		print("[Scanner] Options: " + options)

		# Extract the root drive
		match = re.search('root=(.*) ', options)

		if match:
			print("[Scanner] Match: " + match.group(1))

		# Not recommended since it creates an explicit dependency to
		# the 'parted' app. I'm not sure if this is desired.
		
		#results = subprocess.Popen(
		#         ["parted", .., "print"]
		#then pipe it to grep and filter out "Partition Style:"

	# Get fstab information. We will use this to get /boot and /
	def scan_fstab(self):
		print("[Scanner] Scanning /etc/fstab")

		r1 = subprocess.Popen(
		          ["cat", "/etc/fstab"],
		          stdout=subprocess.PIPE,
		          universal_newlines=True)

		r2 = subprocess.Popen(
		          ["grep", "-E", "/boot"],
		          stdin=r1.stdout,
		          stdout=subprocess.PIPE,
		          universal_newlines=True)

		out = r2.stdout.readlines()

		if out:
			for i in out:
				print(i.strip())
				self.__fstab_vals.append(i.strip())

		for i in self.__fstab_vals:
			for x in i.split():
				print("again: " + x)

	# Returns the kernel set that was gathered
	def get_kernels(self):
		self.find_kernels()
		return self.__kernels

	# Prints a list of detected kernels in the boot directory
	def print_kernels(self):
		print("[Scanner] Kernels detected in boot directory:")

		for i in self.__kernels:
			print("[Scanner] " + i)
