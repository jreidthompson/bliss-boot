# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from etc import conf

class Toolkit(object):
	# Creates a symlink in /boot that points back to itself
	def create_bootlink(self):
		if not os.path.exists("/boot/boot"):
			os.chdir("/boot")
			os.symlink(".", "boot")

	# Cleanly exit the application
	def die(self, message):
		print("[Error] " + message + ". Exiting ...")

		# Remove the incomplete bootloader file
		if conf.bootloader == "grub2":
			if os.path.exists("grub.cfg"):
				os.remove("grub.cfg")

		quit(5)

	# Let's the user know that we are starting
	def start_message(self):
		print("[Toolkit] Starting!")

	# Let's the user know that we are done
	def complete_message(self):
		print("[Toolkit] Complete!")
