# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Kernel Path and Bootloader Type
bootdir = "/boot/kernels"

# Supported bootloaders: grub2, extlinux
bootloader = "grub2"

# 'timeout' is automatically multiplied by 10 for extlinux
timeout = "3"

default = "3.12.10-KS.01"

# GRUB 2 specific settings
efi = 0

# Extlinux specific settings
el_ui = "menu.c32"
el_m_title = "Boot Menu"
el_c_title = "1;37;40"
el_c_border = "30;40"
el_c_unsel = "37;40"

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
	"3.12.11-KS.01" : "root=/dev/sda1 options='ro'",
	"3.12.12-KS.01" : "root=/dev/sda1 options='ro'",
}
