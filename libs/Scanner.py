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
		self.__lvm = 0
		self.__gpt = 0
		self.__dos = 0
		self.__none = 0

	def find_kernels(self):
		print("[Scanner] Scanning: " + conf.bootdir) 

		# Check to see if our boot directory exists before starting
		if not os.path.exists(conf.bootdir):
			os.mkdir(conf.bootdir)

			if not os.path.exists(conf.bootdir):
				self.toolkit.die("Kernel boot directory doesn't exist")
			else:
				print("[Scanner] " + conf.bootdir + " has been created.")

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

	# Get fstab information. We will use this to get /boot
	def scan_fstab(self):
		print("[Scanner] Scanning /etc/fstab for /boot ...")

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
				self.__fstab_vals.append(x.strip())
		else:
			self.toolkit.die("/boot could not be found in /etc/fstab")
	
	# Detect the partition style (gpt or mbr) and 
	# returns either "gpt" or "msdos" as a string
	def detect_layout(self):
		print("[Scanner] Detecting partition layout ...")

		drive = self.__fstab_vals[0]

		# Remove the partition number so that we can find the
		# style of the drive itself
		temp = re.sub("\d$", " ", drive)

		if temp:
			# use blkid /dev/<drive> and get PTTYPE
			# example: blkid /dev/vda: -> /dev/vda: PTTYPE="gpt"
			r1 = subprocess.Popen(
			["blkid", temp.strip()],
			stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			universal_newlines=True)

			r2 = subprocess.Popen(
			["cut", "-d", "\"", "-f", "2"],
			stdin=r1.stdout, stdout=subprocess.PIPE,
			universal_newlines=True)

			out = r2.stdout.readlines()

			if out:
				if out[0].strip() == "gpt":
					self.__gpt = 1
					return "gpt"
				elif out[0].strip() == "dos":
					self.__dos = 1
					return "msdos"
				else:
					self.__none = 1
					return "none"
			else:
				self.toolkit.die("Partition Layout could not be " + 
				"detected for: " + temp)
		else:
			self.toolkit.die("Could not find the value assigned to " + 
			"this boot drive.")

	# Converts the fstab /boot drive entry to a grub 2 compatible format
	# and returns it as a string: (gpt) /dev/sda1 -> (hd0,gpt1)
	def get_bootdrive(self):
		# First let's find the /boot in /etc/fstab
		self.scan_fstab()

		# Get the partition layout/style for this drive (gpt, msdos, or none)
		layout = self.detect_layout()

		if self.__fstab_vals:
			drive = self.__fstab_vals[0]

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
						alphindex = self.toolkit.get_alph_index(alph.group(0))

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
					# contruct it here and return it
					return "(md/" + m1.group(1) + ")"

				# --- LVM: mapper/<volume_group>-<logical_volume> ---
				print("MG1: " + match.group())
				m1 = re.search('mapper/(\w.-\w+)', match.group(1))

				if m1:
					self.__lvm = 1
					return "(lvm/" + m1.group(1) + ")"

				# --- LVM: <volume_group>/<logical_volume> ---
				m1 = re.search('(\w+)/(\w+)', match.group(1))

				if m1:
					self.__lvm = 1
					return "(lvm/" + m1.group(1) + "-" + m1.group(2) + ")"

				# If the auto detection failed, let the user know to
				# explictly set it
				self.toolkit.die("Could not generate the appropriate " +
				"bootdir entry. Please enter it manually in etc/conf.py")

	# Returns 1 if lvm was detected in the above bootdir
	def get_layout(self):
		if self.__gpt == 1:
			return "gpt"
		elif self.__dos == 1:
			return "msdos"
		elif self.__none == 1:
			return "none"
	
	def lvm_status(self):
		if self.__lvm == 1:
			return self.__lvm

	# Returns the kernel set that was gathered
	def get_kernels(self):
		self.find_kernels()
		return self.__kernels

	# Prints a list of detected kernels in the boot directory
	def print_kernels(self):
		print("[Scanner] Kernels detected in boot directory:")

		for i in self.__kernels:
			print("[Scanner] " + i)
