# Copyright (C) 2014-2019 Jonathan Vasquez <jon@xyinn.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ---------- Kernels & Options ----------
# Label, Version, 1 = Default Kernel (others are 0), Name of Kernel, Name of Initrd, Kernel Options
# Example:
#          ('Gentoo', '3.14.27-KS.01', 1, 'vmlinuz', 'initrd', 'root=/dev/sda1 quiet'),
#          ('Gentoo', '3.12.20-KS.11', 0, 'vmlinuz', 'initrd-3.12.20-KS.11', 'root=/dev/sda1 ro quiet'),

kernels = (
    ('Gentoo', '3.14.27-KS.01', 1, 'vmlinuz', 'initrd', 'root=/dev/sda1 quiet'),
)


#---------- General Configuration ----------

# Kernel Path
kernelDirectory = "/boot/kernels"

# Bootloader Type: Supported: [grub2, extlinux]
bootloader = "grub2"

# Is an initrd being used?
useInitrd = 1

# 'timeout' is automatically multiplied by 10 for extlinux
timeout = 3

# If using 'whole disk zfs', dataset where your /boot directory is in
wholeDiskZfsBootPool = "tank/gentoo/root"


#---------- GRUB 2 settings ----------

# If you are using an UEFI system and booting into an UEFI-enabled
# Linux install, enable this
efi = 0

# Only activate this if you are using 'whole disk zfs'
# aka no /boot, and your /boot directory is inside the zfs pool
wholeDiskZfs = 0

# Adds all the modules specified on the list to the grub config
# Feel free to specify or remove anything you use/don't use
goodyBag = [
    #"lvm",
    #"luks",
    #"mdadm",
    #"mdraid09",
    #"mdraid1x",
]


#---------- extlinux settings ----------
extlinuxUi = "menu.c32"
extlinuxMenuTitle = "Boot Menu"
extlinuxTitleColor = "1;37;40"
extlinuxBorderColor = "30;40"
extlinuxUnselectedColor = "37;40"

# If you enable this, it will disable the menu and automatically
# boot your chosen default kernel. Leaving this at 0 will still boot
# automatically but it will first show the menu, wait the timeout value
# that you set above, and then boot the default kernel
extlinuxAutoBoot = 0


# ---------- Other ----------

# Entries below will be appended (as is) to the end of the final file
# Use this if you have custom stuff not detected by the bootloader
# (like Windows installations...)

append = 0

appendStuff = \
"""menuentry "Windows 7" {
    insmod chain

    set root='(hd0,msdos2)'
    chainloader +1
}
"""
