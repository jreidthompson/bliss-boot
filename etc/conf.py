# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Kernel Path and Bootloader Type
bootdir = "/boot/kernels"
bootloader = "grub2"

# GRUB 2 Specific Settings
timeout = "3"
default = "3.12.9-KS.01"

# Kernels
kernels = {
	"3.12.9-KS.01" : "root=/dev/sda1 options='ro'",
	"3.12.9-KS.02" : "root=/dev/sda2 options='ro'",
	"3.12.10-KS.03" : "root=/dev/sda3 options='ro'",
	"3.13.1-KS.04" : "root=/dev/sda4 options='ro'",
}
