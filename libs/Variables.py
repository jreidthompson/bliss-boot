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

import libs.ConfigLoader as ConfigLoader

config = ConfigLoader.GetConfigModule()

# Program Information
name = "Bliss Boot"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "2.0.0"
license = "Apache License 2.0"

# Program Locations
grub2 = "/usr/sbin/grub2-install"
extlinux = "/sbin/extlinux"
sgdisk = "/usr/sbin/sgdisk"

extlinuxGptFirmware = "/usr/share/syslinux/gptmbr.bin"
extlinuxMbrFirmware = "/usr/share/syslinux/mbr.bin"
extlinuxUi = "/usr/share/syslinux/" + config.extlinuxUi
extlinuxLibUtil = "/usr/share/syslinux/libutil.c32"