# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

import os
import sys
import re

from subprocess import call
from subprocess import check_output

import libs.Variables as var

# Provides basic utilities that can be used by any class (Colorized printing, parameter retrieval, etc)
class Tools(object):
    _force = 0
    _outputFile = ""
    _bootloaderDrive = ""
    _useGrub2 = 0
    _useExtlinux = 0
    _extlinuxBootDirPath = "/boot/extlinux"
    _onlyBootloader = 0

    _options = (
        ("-o", "--output"),
        ("-f", "--force"),
        ("-d", "--drive"),
        ("-E", "--install-extlinux"),
        ("-G", "--install-grub2"),
        ("-B", "--only-bootloader"),
        ("-h", "--help"),
    )

    # Checks to see if a parameter is a valid flag
    @classmethod
    def IsFlag(cls, vParam):
        for i in range(len(cls._options)):
            for j in range(len(cls._options[i])):
                if cls._options[i][j] == vParam:
                        return 0

        return -1

    # Checks parameters and running user
    @classmethod
    def ProcessArguments(cls):
        user = check_output(["whoami"], universal_newlines=True).strip()

        if user != "root":
            cls.Fail("This program must be ran as root")

        arguments = sys.argv[1:]

        if len(arguments) >= 1:
            for i in range(len(arguments)):
                # Sets the output file to write the config to
                if arguments[i] == "-o" or arguments[i] == "--output":
                    try:
                        if cls.IsFlag(arguments[i+1]) != 0:
                            cls._outputFile = arguments[i+1]
                    except IndexError:
                        cls.Fail("You need to pass a path to output the file!")

                # Set 'force' in order to overwrite output file target
                elif arguments[i] == "-f" or arguments[i] == "--force":
                    cls._force = 1

                # Set the drive where we want to install the bootloader
                elif arguments[i] == "-d" or arguments[i] == "--drive":
                    try:
                        if cls.IsFlag(arguments[i+1]) != 0:
                            cls._unmappedBootloaderDrive = arguments[i+1]
                            cls._bootloaderDrive = cls.GetDriveRoot(cls.MapIdentifierToDrive(cls._unmappedBootloaderDrive))
                    except IndexError:
                        pass

                # Let the program know that we want to install extlinux
                elif arguments[i] == "-E" or arguments[i] == "--install-extlinux":
                    cls._useExtlinux = 1

                    try:
                        if cls.IsFlag(arguments[i+1]) != 0:
                            cls._extlinuxBootDirPath = arguments[i+1]
                    except IndexError:
                        pass

                # Let the program know that we want to install GRUB 2
                elif arguments[i] == "-G" or arguments[i] == "--install-grub2":
                    cls._useGrub2 = 1

                # Displays the help/usage message
                elif arguments[i] == "-h" or arguments[i] == "--help":
                    cls.PrintUsage()

                # Sets the tasks to do (bootloader|config only, or both)
                elif arguments[i] == "-B" or arguments[i] == "--only-bootloader":
                    cls._onlyBootloader = 1

    # Processes a UUID/PARTUUID= field in order to find out where the real drive is,
    # instead of the traditional /dev/sda, /dev/md0 references
    @classmethod
    def MapIdentifierToDrive(cls, vIdValue):
        splitResults = vIdValue.split("=")

        targetDrive = ""

        for i in range(len(splitResults)):
            if splitResults[i] == "UUID":
                targetDrive = cls.GetDriveFromIdentifier("UUID", splitResults[i+1])
                break
            elif splitResults[i] == "PARTUUID":
                targetDrive = cls.GetDriveFromIdentifier("PARTUUID", splitResults[i+1])
                break

        # If we aren't using anything fancy like UUID=, then the
        # boot drive field and the split results will be the same
        if vIdValue == ''.join(splitResults):
            targetDrive = vIdValue

        return targetDrive

    # Returns the drive matching this identifier
    @classmethod
    def GetDriveFromIdentifier(cls, vId, vValue):
        cmd = 'blkid -o full -s ' + vId + ' | grep ' + vValue + ' | cut -d ":" -f 1'
        results = check_output(cmd, shell=True, universal_newlines=True).strip()

        if results:
            return results
        else:
            Tools.Fail("No drives were found with the " + vValue + " value.")

     # Returns the drive root (i.e /dev/sda)
    @classmethod
    def GetDriveRoot(cls, vDrive):
        # Remove the partition number so that we can find the drive root
        match = re.sub("\d$", "", vDrive)

        if match:
            return match

        return -1

    # Returns only the number of the boot drive
    @classmethod
    def GetDriveRootNumber(cls, vDrive):
        # This is the partition number which will be used to set the
        # Legacy BIOS Bootable flag if the user uses extlinux and it's GPT
        partitionNumber = re.search("\d+", vDrive)

        if partitionNumber:
            return partitionNumber.group()

        Tools.Warn("Skipping extlinux bootloader installation since your /boot (" + vDrive + ") is probably on LVM.")
        return -1

    # Prints the header of the application
    @classmethod
    def PrintHeader(cls):
        cls.Print(cls.Colorize("yellow", "----------------------------------"))
        cls.Print(cls.Colorize("yellow", var.name + " - v" + var.version))
        cls.Print(cls.Colorize("yellow", var.contact))
        cls.Print(cls.Colorize("yellow", "Licensed under the " + var.license))
        cls.Print(cls.Colorize("yellow", "----------------------------------") + "\n")

    # Prints the usage information
    @classmethod
    def PrintUsage(cls):
        print("Usage: bliss-boot [OPTION]\n")
        print("-o, --output\t\t\tGenerates the configuration file at this location.\n")
        print("-f, --force\t\t\tOverwrites the file at the target output path.\n")
        print("-d, --drive\t\t\tSpecifies the target drive to install the bootloader at.\n")
        print("-B, --only-bootloader\t\tOnly installs the bootloader, doesn't generate the config file.\n")
        print("-E, --install-extlinux\t\tInstalls extlinux and the MBR to the target path on disk and /boot drive (in fstab).")
        print("\t\t\t\tExample: bliss-boot -E (optional: target folder) (optional: -d <drive>)\n")
        print("-G, --install-grub2\t\tInstalls grub 2 to your drive")
        print("\t\t\t\tExample: bliss-boot -G (optional: -d <drive>)\n")
        print("-h, --help\t\t\tPrints this help message and then exits.\n")
        quit()

    # Cleanly exit the application
    @classmethod
    def Fail(cls, vMessage):
        call(["echo", "-e", cls.Colorize("red", vMessage)])
        quit(1)

     # Returns the string with a color to be used in bash
    @classmethod
    def Colorize(cls, vColor, vMessage):
        if vColor == "red":
            colored_message = "\e[1;31m" + vMessage + "\e[0;m"
        elif vColor == "yellow":
            colored_message = "\e[1;33m" + vMessage + "\e[0;m"
        elif vColor == "green":
            colored_message = "\e[1;32m" + vMessage + "\e[0;m"
        elif vColor == "cyan":
            colored_message = "\e[1;36m" + vMessage + "\e[0;m"
        elif vColor == "purple":
            colored_message = "\e[1;34m" + vMessage + "\e[0;m"
        elif vColor == "none":
            colored_message = vMessage

        return colored_message

    # Prints a message
    @classmethod
    def Print(cls, vMessage):
        call(["echo", "-e", cls.Colorize("cyan", vMessage)])

    # Used for successful entries
    @classmethod
    def Success(cls, vMessage):
        call(["echo", "-e", cls.Colorize("green", vMessage)])

    # Used for warnings
    @classmethod
    def Warn(cls, vMessage):
        call(["echo", "-e", cls.Colorize("yellow", vMessage)])

    # Returns the value of whether or not GRUB 2 will be installed
    @classmethod
    def IsGrub2(cls):
        return cls._useGrub2

    # Returns the value of whether or not extlinux will be installed
    @classmethod
    def IsExtlinux(cls):
        return cls._useExtlinux

    # Returns a positive number if an output option was set
    @classmethod
    def IsOutputSet(cls):
        if cls._outputFile:
            return 1

        return 0

    # Gets the desired output path
    @classmethod
    def GetOutputFile(cls):
        return cls._outputFile

    # Returns the value of whether or not we will overwrite the output file if it exists.
    @classmethod
    def IsForceSet(cls):
        return cls._force

    # Returns directory where extlinux installs its files
    @classmethod
    def GetExtlinuxBootDirPath(cls):
        return cls._extlinuxBootDirPath

    # Sets the bootloader drive
    @classmethod
    def SetBootloaderDrive(cls, vDrive):
        cls._bootloaderDrive = vDrive

    # Returns the bootloader drive
    @classmethod
    def GetBootloaderDrive(cls):
        return cls._bootloaderDrive

    # Returns if we are only going to install the bootloader
    @classmethod
    def OnlyInstallBootloader(cls):
        return cls._onlyBootloader
