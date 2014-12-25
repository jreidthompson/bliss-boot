# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
default = "3.14.27-KS.01"

# What do you want your kernel/initrd to be called in the config file?
kernel_prefix = "vmlinuz"
initrd_prefix = "initrd"

# If using 'whole disk zfs', dataset where your /boot directory is in
zfs_boot = "tank/gentoo/root"


#---------- GRUB 2 settings ----------

# If you are using an UEFI system and booting into an UEFI-enabled
# Linux install, enable this
efi = 0

# Only activate this if you are using 'whole disk zfs'
# aka no /boot, and your /boot directory is inside the zfs pool
zfs = 0

# Adds all the modules specified on the list to the grub config
# Feel free to specify or remove anything you use/don't use
goody_bag = [
    #"lvm",
    #"luks",
    #"mdadm",
    #"mdraid09",
    #"mdraid1x",
]


#---------- extlinux settings ----------
el_ui = "menu.c32"
el_m_title = "Boot Menu"
el_c_title = "1;37;40"
el_c_border = "30;40"
el_c_unsel = "37;40"

# If you enable this, it will disable the menu and automatically
# boot your chosen default kernel. Leaving this at 0 will still boot
# automatically but it will first show the menu, wait the timeout value
# that you set above, and then boot the default kernel
el_auto_boot = 0


# ---------- Kernels & Options ----------
kernels = (
    ('Gentoo', '3.12.18-KS.01', 'root=/dev/sda1 quiet'),
)


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
