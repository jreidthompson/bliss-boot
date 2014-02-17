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
timeout = 3

# Default kernel to boot into
default = "3.12.11-KS.01"

# GRUB 2 specific settings
efi = 0

# Only activate this if you are using 'whole disk zfs'
# aka no /boot, and your /boot directory is inside the zfs pool
zfs = 0

# Dataset where your /boot directory is in
zfs_boot = "tank/os/funtoo/root"

# Extlinux specific settings
el_ui = "menu.c32"
el_m_title = "Boot Menu"
el_c_title = "1;37;40"
el_c_border = "30;40"
el_c_unsel = "37;40"

# Add your kernels and options here
kernels = {
	"3.12.11-KS.01" : "root=/dev/sda1 options='ro' quiet",
}
