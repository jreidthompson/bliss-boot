# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import libs.ConfigLoader as ConfigLoader

config = ConfigLoader.GetConfigModule()

# Program Information
name = "Bliss Boot"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "2.0.2"
license = "MPL 2.0"

# Program Locations
grub2 = "/usr/sbin/grub2-install"
extlinux = "/sbin/extlinux"
sgdisk = "/usr/sbin/sgdisk"

extlinuxGptFirmware = "/usr/share/syslinux/gptmbr.bin"
extlinuxMbrFirmware = "/usr/share/syslinux/mbr.bin"
extlinuxUi = "/usr/share/syslinux/" + config.extlinuxUi
extlinuxLibUtil = "/usr/share/syslinux/libutil.c32"
