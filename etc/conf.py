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
default = "3.12.10-KS.03"

# 'bootdrive' format examples:
# /dev/sda        (hd0)
# /dev/sda1       (hd0,1) (hd0, gpt1) or (hd0, msdos1) depending if gpt/mbr
# /dev/sdb3       (hd1,3)
# /dev/md0        (md/0)
bootdrive = "(hd0, gpt1)"

# Add your kernels and options here
kernels = {
	"3.12.9-KS.01" : "root=/dev/mapper/vg-one1 options='ro'",
	"3.12.9-KS.02" : "root=/dev/sda2 options='ro'",
	"3.12.10-KS.03" : "root=/dev/sda3 options='ro'",
	"3.13.1-KS.04" : "root=/dev/sda4 options='ro'",
}
