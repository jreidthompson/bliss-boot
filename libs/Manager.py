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

import os

from libs.Tools import Tools
from libs.Scanner import Scanner
from libs.Installer import Installer

import libs.ConfigLoader as ConfigLoader
import libs.Variables as var

config = ConfigLoader.GetConfigModule()

class Manager(object):
    # Generates the bootloader configuration
    @classmethod
    def WriteEntries(cls):
        outputFile = ""
        driveLayout = Scanner.GetDriveLayout()
        isOutput = Tools.IsOutputSet()

        if isOutput:
            outputFile = Tools.GetOutputFile()

            # Check to see if the directory for this file exists. If it doesn't
            # create any directories leading up to the output file so that we don't
            # get a "FileNotFoundError" later on
            outputFileFullPath = os.path.abspath(outputFile)
            outputFileParentDir = os.path.dirname(outputFileFullPath)

            if not os.path.exists(outputFileParentDir):
                cls.CreateOutputDirectory(outputFileParentDir)

        elif not isOutput and config.bootloader == "grub2":
            outputFile = "grub.cfg"
        elif not isOutput and config.bootloader == "extlinux":
            outputFile = "extlinux.conf"

        # Check to see what's the bootloader before we start adding
        # all the entries, depending the bootloader we can cleanly start
        # adding generic information like default kernel, timeouts, etc
        position = Scanner.FindDefaultKernel()

        if position != -1:
            if config.bootloader == "grub2":
                Tools.Print("Generating GRUB 2 configuration ...")

                bootdrive = Scanner.GetGrub2BootDrive()

                if os.path.exists(outputFile):
                    if Tools.IsForceSet():
                        dossier = open(outputFile, "w")
                    else:
                        Tools.Fail("Target file: " + outputFile + " already exists. Pass -f to overwrite.")
                else:
                    dossier = open(outputFile, "w")

                dossier.write("set timeout=" + str(config.timeout) + "\n")
                dossier.write("set default=" + str(position) + "\n")
                dossier.write("\n")

                # Write the modules that need to be inserted depending
                # drive style. For whole disk zfs, none will be returned
                # since a person can partition the drive manually and use msdos,
                # or they can let zfs format their drive automatically with
                # gpt. This ambiguity will be the reason both grub modules will
                # be inserted.

                if driveLayout == "gpt":
                    dossier.write("insmod part_gpt\n")
                elif driveLayout == "msdos":
                    dossier.write("insmod part_msdos\n")
                elif driveLayout == "none":
                    dossier.write("insmod part_gpt\n")
                    dossier.write("insmod part_msdos\n")

                if config.efi:
                    dossier.write("insmod efi_gop\n")
                    dossier.write("insmod efi_uga\n")
                    dossier.write("insmod fat\n")

                if config.wholeDiskZfs:
                    dossier.write("insmod zfs\n")

                if config.goodyBag:
                    for candy in config.goodyBag:
                        dossier.write("insmod " + candy + "\n")

                if not config.wholeDiskZfs:
                    dossier.write("\nset root='" + bootdrive + "'\n")

                dossier.write("\n")
                dossier.close()
            elif config.bootloader == "extlinux":
                Tools.Print("Generating extlinux configuration ...")

                # Gets the name of the default kernel
                defaultKernelLabel = Scanner.GetKernel(position)[0]

                if os.path.exists(outputFile):
                    if Tools.IsForceSet():
                        dossier = open(outputFile, "w")
                    else:
                        Tools.Fail("Target file: " + outputFile + " already exists. Pass -f to overwrite.")
                else:
                    dossier = open(outputFile, "w")

                dossier.write("TIMEOUT " + str(int(config.timeout * 10)) + "\n")

                if not config.extlinuxAutoBoot:
                    dossier.write("UI " + config.extlinuxUi + "\n")

                dossier.write("\n")
                dossier.write("DEFAULT " + defaultKernelLabel + str(position) + "\n\n")
                dossier.write("MENU TITLE " + config.extlinuxMenuTitle + "\n")
                dossier.write("MENU COLOR title " + config.extlinuxTitleColor + "\n")
                dossier.write("MENU COLOR border " + config.extlinuxBorderColor + "\n")
                dossier.write("MENU COLOR unsel " + config.extlinuxUnselectedColor + "\n")
                dossier.write("\n")
                dossier.close()
            else:
                Tools.Fail("The bootloader defined in " + ConfigLoader.GetConfigFilePath() + " is not supported.")
        else:
            Tools.Fail("The default kernel entry in " + ConfigLoader.GetConfigFilePath() + " was not found in " + config.kernelDirectory)

        # Add all our desired kernels
        for kernel in Scanner.GetCommonKernels():
            # Get the position so that we can create the labels correctly
            position = Scanner.GetKernelIndexInCommonList(kernel)

            Tools.Success("Adding: " + kernel[0] + " - " + kernel[1])

            cs = cls.StripHead(config.kernelDirectory)
            kernelPath = cs + "/" + kernel[1]

            # Depending the bootloader we have specified, generate
            # its appropriate configuration.
            if config.bootloader == "grub2":
                # Open it in append mode since the header was previously
                # created before.
                dossier = open(outputFile, "a")
                dossier.write("menuentry \"" + kernel[0] + " - " + kernel[1] + "\" {\n")

                if config.wholeDiskZfs:
                    dossier.write("\tlinux " + bootdrive + "/@" + kernelPath + "/" + kernel[3] + " " + kernel[5] + "\n")

                    if config.useInitrd:
                        dossier.write("\tinitrd " + bootdrive + "/@" + kernelPath + "/" + kernel[4] + "\n")

                else:
                    dossier.write("\tlinux " + kernelPath + "/" + kernel[3] + " " + kernel[5] + "\n")

                    if config.useInitrd:
                        dossier.write("\tinitrd " + kernelPath + "/" + kernel[4] + "\n")

                dossier.write("}\n\n")
                dossier.close()
            elif config.bootloader == "extlinux":
                dossier = open(outputFile, "a")
                dossier.write("LABEL " + kernel[0] + str(position) + "\n")
                dossier.write("\tMENU LABEL " + kernel[0] + " - " + kernel[1] + "\n")
                dossier.write("\tLINUX " + kernelPath + "/" + kernel[3] + "\n")

                if config.useInitrd:
                    dossier.write("\tINITRD " + kernelPath + "/" + kernel[4] + "\n")

                dossier.write("\tAPPEND " + kernel[5] + "\n")
                dossier.write("\n")
                dossier.close()

        # Append anything else the user wants automatically added
        if config.append and config.appendStuff:
            Tools.Print("Appending additional information ...")

            if config.bootloader == "grub2":
                dossier = open(outputFile, "a")
                dossier.write(config.appendStuff)
                dossier.close()
            elif config.bootloader == "extlinux":
                dossier = open(outputFile, "a")
                dossier.write(config.appendStuff)
                dossier.close()

        # Check to make sure that the file was created successfully.
        # If so let the user know..
        if os.path.isfile(outputFile):
            Tools.Success("'" + outputFile + "' has been created!")
        else:
            Tools.Fail("Either the file couldn't be created or the specified bootloader isn't supported.")

    # Triggers bootloader installation
    @classmethod
    def InstallBootloader(cls):
        # Set the drive using the /boot entry in /etc/fstab if the user wants
        # to install a bootloader but didn't specify the drive themselves as an argument.
        if not Tools.GetBootloaderDrive():
            installer = Installer(Tools.GetDriveRoot(Scanner._bootDrive))
        else:
            installer = Installer(Tools.GetBootloaderDrive())

        # Set extlinux specific information before we start
        if installer.GetBootloader() == "extlinux":
            installer.SetDriveNumber(Tools.GetDriveRootNumber(Scanner._bootDrive))
            installer.SetDriveType(Scanner.GetDriveLayout())

        installer.start()

    # Strips the first directory of the path passed. Used to get a good path and not need
    # a boot symlink in /boot
    @classmethod
    def StripHead(cls, vPath):
        if vPath:
            splinters = vPath.split("/")
            srange = len(splinters)

            if srange >= 3:
                news = ""

                for i in range(len(splinters))[2:]:
                    news = news + "/" + splinters[i]

                return news
            elif srange == 2:
                # if two then that means we will be looking in that folder specifically for kernels
                # so just return /
                return "/"
        else:
            Tools.Fail("The value to strip is empty ...")

    # Creates all the directories needed so that the output file can be written
    @classmethod
    def CreateOutputDirectory(cls, vParentDirectory):
        if not os.path.exists(vParentDirectory):
            os.makedirs(vParentDirectory)

            if not os.path.exists(vParentDirectory):
                Tools.Fail("Unable to create the " + vParentDirectory + " directory ...")
