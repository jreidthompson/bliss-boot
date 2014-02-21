# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#---------- General Configuration ----------

# Kernel Path and Bootloader Type
bootdir = "/boot/kernels"

# Supported bootloaders: grub2, extlinux
bootloader = "grub2"

# Is an initrd being used?
initrd = 1

# 'timeout' is automatically multiplied by 10 for extlinux
timeout = 3

# Default kernel to boot into
default = "3.12.12-KS.01"

# If using 'whole disk zfs', dataset where your /boot directory is in
zfs_boot = "tank/os/funtoo/root"


#---------- GRUB 2 settings ----------

# If you are using an UEFI system and booting into an UEFI-enabled
# Linux install, enable this
efi = 0

# Only activate this if you are using 'whole disk zfs'
# aka no /boot, and your /boot directory is inside the zfs pool
zfs = 0


#---------- extlinux settings ----------
el_ui = "menu.c32"
el_m_title = "Boot Menu"
el_c_title = "1;37;40"
el_c_border = "30;40"
el_c_unsel = "37;40"


# ---------- Kernels & Options ----------
kernels = {
	'3.12.12-KS.01' : 'root=/dev/sda1 options="ro" quiet',
}


# ---------- Other ----------

# Entries below will be appended (as is) to the end of the final file
# Use this if you have custom stuff not detected by the bootloader
# (like Windows installations...)

append = 0

append_stuff = \
"""menuentry "Windows 7" {
	insmod chain

	set root='(hd0,msdos2)'
	chainloader +1
}
"""
