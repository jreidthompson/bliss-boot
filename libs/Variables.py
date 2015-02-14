# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

import libs.ConfigLoader as ConfigLoader

config = ConfigLoader.GetConfigModule()

# Program Information
name = "Bliss Boot"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "2.0.3"
license = "Simplified BSD License"

# Program Locations
grub2 = "/usr/sbin/grub2-install"
extlinux = "/sbin/extlinux"
sgdisk = "/usr/sbin/sgdisk"

extlinuxGptFirmware = "/usr/share/syslinux/gptmbr.bin"
extlinuxMbrFirmware = "/usr/share/syslinux/mbr.bin"
extlinuxUi = "/usr/share/syslinux/" + config.extlinuxUi
extlinuxLibUtil = "/usr/share/syslinux/libutil.c32"
