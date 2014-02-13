# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess

from etc import conf

class Scanner(object):
	__kernels = set()

	def __init__(self):
		print("[Scanner] Activated")

	def find_kernels(self):
		print("[Scanner] Scanning: " + conf.bootdir) 

		results = subprocess.Popen(
		          ["ls", conf.bootdir],
				  stdout=subprocess.PIPE,
		          universal_newlines=True)
		
		ou = results.stdout.readlines()

		# Add kernels to out kernel set
		if ou:
			for i in ou:
				self.__kernels.add(i.strip())
		
	def print_kernels(self):
		print("[Scanner] Kernels Detected: ")

		for i in self.__kernels:
			print("[Scanner] Kernel: " + i)

	def get_kernels(self):
		return self.__kernels
