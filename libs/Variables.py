# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from libs.ConfigLoader import ConfigLoader

config = ConfigLoader.get_config()

# Program Information
name = "Bliss Boot"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "1.1.0"
license = "MPL 2.0"

# Program Locations
grub2 = "/usr/sbin/grub2-install"
extlinux = "/sbin/extlinux"
sgdisk = "/usr/sbin/sgdisk"

el_gpt_firm = "/usr/share/syslinux/gptmbr.bin"
el_mbr_firm = "/usr/share/syslinux/mbr.bin"
el_ui = "/usr/share/syslinux/" + config.el_ui
el_libutil = "/usr/share/syslinux/libutil.c32"
