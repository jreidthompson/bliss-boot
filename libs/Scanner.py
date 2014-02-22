# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import re

from libs.Toolkit import Toolkit
from etc import conf

tools = Toolkit()

class Scanner(object):
	def __init__(self):
		self.kernels = []
		self.fstab_vals = []

	def find_kernels(self):
		tools.eprint("Scanner", "Scanning " + conf.bootdir + " ...") 

		# Check to see if our boot directory exists before starting
		if not os.path.exists(conf.bootdir):
			tools.eprint("Scanner", conf.bootdir + " doesn't exist. " +
			"Creating ...")

			os.mkdir(conf.bootdir)

			if not os.path.exists(conf.bootdir):
				tools.die(conf.bootdir + " directory doesn't exist")
			else:
				tools.esucc("[Scanner] " + conf.bootdir +
				              " has been created.")

		results = subprocess.Popen(
		          ["ls", conf.bootdir],
		          stdout=subprocess.PIPE,
		          universal_newlines=True)
		
		out = results.stdout.readlines()

		# Add kernels to out kernel set
		if out:
			for i in out:
				self.kernels.append(i.strip())
		else:
			tools.die("No kernels found in " + conf.bootdir)

	# Get fstab information. We will use this to get /boot
	def scan_fstab(self):
		tools.eprint("Scanner", "Scanning /etc/fstab for /boot ...")

		r1 = subprocess.Popen(
			 ["cat", "/etc/fstab"],
			 stdout=subprocess.PIPE,
			 universal_newlines=True)

		r2 = subprocess.Popen(
			 ["grep", "/boot[[:blank:]]"],
			 stdin=r1.stdout,
			 stdout=subprocess.PIPE,
			 universal_newlines=True)

		r3 = subprocess.Popen(
			 ["awk", "{print $1, $2, $3, $4, $5, $6}"],
			 stdin=r2.stdout, stdout=subprocess.PIPE,
			 universal_newlines=True)

		out = r3.stdout.readlines()

		if out:
			# Split the /boot line so we can store it
			splits = out[0].split()

			# Save fstab /boot drive info
			for x in splits:
				self.fstab_vals.append(x.strip())
		else:
			tools.die("/boot could not be found in /etc/fstab")

	# Converts the fstab /boot drive entry to a grub 2 compatible format
	# and returns it as a string: (gpt) /dev/sda1 -> (hd0,gpt1)
	def get_bootdrive(self):
		# If we are using 'whole disk zfs', then we won't have a /boot entry
		# in /etc/fstab. So instead we will format the zfs_boot variable and
		# return it ready to be used in grub2
		if conf.zfs == 1:
			match = re.search('(/[a-zA-Z0-9_/]+)', conf.zfs_boot)

			if match:
				return match.group()

			tools.die("Could not parse the 'zfs_boot' variable " +
			"correctly.")

		# First let's find the /boot in /etc/fstab
		self.scan_fstab()

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
						cval = cval + "," + layout

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

				# If the auto detection failed, let the user know to
				# explictly set it
				tools.die("Could not generate the appropriate " +
				"bootdir entry. Please enter it manually in etc/conf.py")

	# Returns the kernel set that was gathered
	def get_kernels(self):
		self.find_kernels()
		return self.kernels

	# Prints a list of detected kernels in the boot directory
	def print_kernels(self):
		tools.eprint("Scanner", "Kernels detected in boot directory:")

		for i in self.kernels:
			tools.eprint("Scanner", i)
