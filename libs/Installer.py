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

import os
import shutil

from subprocess import call
from libs.Toolkit import Toolkit as tools

import libs.Variables as var

class Installer(object):
    def __init__(self, drive):
        self.grub2 = tools.is_grub2()
        self.extlinux = tools.is_extlinux()
        self.bootloader = self.get_boot_install()
        self.drive = drive

        # Extlinux
        self.path = tools.get_el_path()
        self.drive_number = -1
        self.drive_type = "none"

    # Starts the bootloader install process
    def start(self):
        if self.bootloader == "grub2":
            self.install_grub2()
        elif self.bootloader == "extlinux":
            self.install_extlinux()
        else:
            tools.ewarn("Skipping bootloader installation ...")

    # Sets the drive's partition number (used for extlinux: example: /dev/sda1 = 1)
    def set_drive_number(self, number):
        self.drive_number = number

    # Gets the drive's partition number
    def get_drive_number(self):
        return self.drive_number

    # Sets the drive's partition layout (gpt, msdos, etc)
    def set_drive_type(self, drive_type):
        self.drive_type = drive_type

    # Gets the drive's partition layout
    def get_drive_type(self):
        return self.drive_type

    # Sets the bootloader we want to install
    def set_bootloader(self, bootloader):
        self.bootloader = bootloader

    # Gets the bootloader we want to install
    def get_bootloader(self):
        return self.bootloader

    # Returns the bootloader to install if any
    def get_boot_install(self):
        if self.grub2 and self.extlinux:
            tools.die("You cannot install both extlinux and grub2 in the same run!")
        elif self.grub2:
            return "grub2"
        elif self.extlinux:
            return "extlinux"

    # Installs GRUB 2
    def install_grub2(self):
        if self.drive:
            tools.eprint("Installing GRUB 2 to " + self.drive + " ...")

            try:
                result = call([var.grub2, self.drive])

                if not result:
                    tools.esucc("GRUB 2 Installed Successfully!")
                else:
                    tools.die("Failed to install GRUB 2 into " + self.drive + " !")

            except FileNotFoundError:
                tools.die("GRUB 2 isn't installed. Please install it and try again!")
        else:
            tools.die("The GRUB 2 drive has not been defined!")

    # Installs Extlinux
    def install_extlinux(self):
        tools.eprint("Installing extlinux to " + self.path + " and writing firmware to " + self.drive + " ...")

        # Make the directory to install extlinux in
        if not os.path.exists(self.path):
            os.makedirs(self.path)

            if not os.path.exists(self.path):
                tools.die("Unable to create the " + self.path + " directory ...")

        # Install extlinux to folder
        try:
            result = call([var.extlinux, "--install", self.path])
        except FileNotFoundError:
            tools.die("extlinux is not installed! Please install it and try again.")

        if not result:
            tools.esucc("extlinux was installed successfully to " + self.path + "!")
        else:
            tools.die("Failed to install extlinux into " + self.path)

        # Copy the menu ui the user specified, and libutil.c32
        el_files = [
            var.el_ui,
            var.el_libutil,
        ]

        for i in el_files:
            if os.path.isfile(i):
                shutil.copy(i, self.path)

                if not os.path.isfile(self.path + "/" + os.path.basename(i)):
                    tools.die("Failed to copy " + os.path.basename(i) + "!")
            else:
                tools.die(os.path.basename(i) + " doesn't exist")

        # GPT
        if self.drive_type == "gpt":
            firm = var.el_gpt_firm

            # Toggle GPT bios bootable flag
            cmd = var.sgdisk + " " + self.drive + " --attributes=" + self.drive_number + ":set:2"
            result = call(cmd, shell=True)

            if not result:
                tools.esucc("Successfully toggled legacy bios bootable flag!")
                cmd = var.sgdisk + " " + self.drive + " --attributes=" + self.drive_number + ":show"

                try:
                    result = call(cmd, shell=True)
                except FileNotfoundError:
                    tools.die("gptfdisk is not installed! Please install it and try again.")
            else:
                tools.die("Error setting legacy bios bootable flag!")
        # MBR
        elif self.drive_type == "msdos":
            firm = var.el_mbr_firm

        # Write the firmware to the drive
        if self.drive_type == "gpt" or self.drive_type == "msdos":
            if os.path.isfile(firm):
                tools.eprint("Writing firmware to " + self.drive + " ...")

                cmd = "dd bs=440 conv=notrunc count=1 if=" + firm + " of=" + self.drive
                result = call(cmd, shell=True)

                if not result:
                    tools.esucc(os.path.basename(firm) + " was successfully written to " + self.drive + "!")
                else:
                    tools.die("Failed to write extlinux firmware to " + self.drive + "!")
        else:
            tools.die("Unable to determine firmware to use for extlinux ...")
