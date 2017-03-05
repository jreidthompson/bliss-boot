# Copyright 2014-2017 Jonathan Vasquez <jon@xyinn.org>
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
