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
default = "3.12.10-KS.01"
efi = 0

# 'bootdrive' format examples:
# /dev/sda        (hd0)
# /dev/sda1       (hd0,gpt1) or (hd0,msdos1)
# /dev/sdb3       (hd1,gpt3) or (hd1,msdos3) 
# /dev/md0        (md/0)

# Leave 'bootdrive' blank for auto detection
bootdrive = ""

# Add your kernels and options here
kernels = {
	"3.12.10-KS.01" : "root=/dev/sda1 options='ro'",
}
