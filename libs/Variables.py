# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

import libs.ConfigLoader as ConfigLoader

config = ConfigLoader.GetConfigModule()

# Program Information
name = "Bliss Boot"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "2.0.1"
license = "GPLv2"

# Program Locations
grub2 = "/usr/sbin/grub2-install"
extlinux = "/sbin/extlinux"
sgdisk = "/usr/sbin/sgdisk"

extlinuxGptFirmware = "/usr/share/syslinux/gptmbr.bin"
extlinuxMbrFirmware = "/usr/share/syslinux/mbr.bin"
extlinuxUi = "/usr/share/syslinux/" + config.extlinuxUi
extlinuxLibUtil = "/usr/share/syslinux/libutil.c32"
