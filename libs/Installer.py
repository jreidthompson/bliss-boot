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
from libs.Tools import Tools

import libs.Variables as var

class Installer(object):
    @classmethod
    def __init__(cls, vDrive):
        cls._useGrub2 = Tools.IsGrub2()
        cls._useExtlinux = Tools.IsExtlinux()

        # Extlinux
        cls._extlinuxBootDirPath = Tools.GetExtlinuxBootDirPath()
        cls._driveNumber = -1
        cls._driveType = "none"
        cls._drive = vDrive
        cls._bootloader = cls.GetBootloaderToInstall()

    # Starts the bootloader install process
    @classmethod
    def start(cls):
        if cls._bootloader == "grub2":
            cls.InstallGrub2()
        elif cls._bootloader == "extlinux":
            cls.InstallExtlinux()
        else:
            Tools.Warn("Skipping bootloader installation ...")

    # Sets the drive's partition number (used for extlinux: example: /dev/sda1 = 1)
    @classmethod
    def SetDriveNumber(cls, vNumber):
        cls._driveNumber = vNumber

    # Gets the drive's partition number
    @classmethod
    def GetDriveNumber(cls):
        return cls._driveNumber

    # Sets the drive's partition layout (gpt, msdos, etc)
    @classmethod
    def SetDriveType(cls, vDriveType):
        cls._driveType = vDriveType

    # Gets the drive's partition layout
    @classmethod
    def GetDriveType(cls):
        return cls._driveType

    # Sets the bootloader we want to install
    @classmethod
    def SetBootloader(cls, vBootloader):
        cls._bootloader = vBootloader

    # Gets the bootloader we want to install
    @classmethod
    def GetBootloader(cls):
        return cls._bootloader

    # Returns the bootloader to install if any
    @classmethod
    def GetBootloaderToInstall(cls):
        if cls._useGrub2 and cls._useExtlinux:
            Tools.Fail("You cannot install both extlinux and grub2 in the same run!")
        elif cls._useGrub2:
            return "grub2"
        elif cls._useExtlinux:
            return "extlinux"

    # Installs GRUB 2
    @classmethod
    def InstallGrub2(cls):
        if cls._drive:
            Tools.Print("Installing GRUB 2 to " + cls._drive + " ...")

            try:
                result = call([var.grub2, cls._drive])

                if not result:
                    Tools.Success("GRUB 2 Installed Successfully!")
                else:
                    Tools.Fail("Failed to install GRUB 2 into " + cls._drive + " !")

            except FileNotFoundError:
                Tools.Fail("GRUB 2 isn't installed. Please install it and try again!")
        else:
            Tools.Fail("The GRUB 2 drive has not been defined!")

    # Installs Extlinux
    @classmethod
    def InstallExtlinux(cls):
        Tools.Print("Installing extlinux to " + cls._extlinuxBootDirPath + " and writing firmware to " + cls._drive + " ...")

        # Make the directory to install extlinux in
        if not os.path.exists(cls._extlinuxBootDirPath):
            os.makedirs(cls._extlinuxBootDirPath)

            if not os.path.exists(cls._extlinuxBootDirPath):
                Tools.Fail("Unable to create the " + cls._extlinuxBootDirPath + " directory ...")

        # Install extlinux to folder
        try:
            result = call([var.extlinux, "--install", cls._extlinuxBootDirPath])
        except FileNotFoundError:
            Tools.Fail("extlinux is not installed! Please install it and try again.")

        if not result:
            Tools.Success("extlinux was installed successfully to " + cls._extlinuxBootDirPath + "!")
        else:
            Tools.Fail("Failed to install extlinux into " + cls._extlinuxBootDirPath)

        # Copy the menu ui the user specified, and libutil.c32
        extlinuxFiles = [
            var.extlinuxUi,
            var.extlinuxLibUtil,
        ]

        for file in extlinuxFiles:
            if os.path.isfile(file):
                shutil.copy(file, cls._extlinuxBootDirPath)

                if not os.path.isfile(cls._extlinuxBootDirPath + "/" + os.path.basename(file)):
                    Tools.Fail("Failed to copy " + os.path.basename(file) + "!")
            else:
                Tools.Fail(os.path.basename(file) + " doesn't exist")

        # GPT
        if cls._driveType == "gpt":
            firm = var.extlinuxGptFirmware

            # Toggle GPT bios bootable flag
            cmd = var.sgdisk + " " + cls._drive + " --attributes=" + cls._driveNumber + ":set:2"
            result = call(cmd, shell=True)

            if not result:
                Tools.Success("Successfully toggled legacy bios bootable flag!")
                cmd = var.sgdisk + " " + cls._drive + " --attributes=" + cls._driveNumber + ":show"

                try:
                    result = call(cmd, shell=True)
                except FileNotfoundError:
                    Tools.Fail("gptfdisk is not installed! Please install it and try again.")
            else:
                Tools.Fail("Error setting legacy bios bootable flag!")
        # MBR
        elif cls._driveType == "msdos":
            firm = var.extlinuxMbrFirmware

        # Write the firmware to the drive
        if cls._driveType == "gpt" or cls._driveType == "msdos":
            if os.path.isfile(firm):
                Tools.Print("Writing firmware to " + cls._drive + " ...")

                cmd = "dd bs=440 conv=notrunc count=1 if=" + firm + " of=" + cls._drive
                result = call(cmd, shell=True)

                if not result:
                    Tools.Success(os.path.basename(firm) + " was successfully written to " + cls._drive + "!")
                else:
                    Tools.Fail("Failed to write extlinux firmware to " + cls._drive + "!")
        else:
            Tools.Fail("Unable to determine firmware to use for extlinux ...")
