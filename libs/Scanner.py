# Copyright (C) 2014-2018 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see<https://www.gnu.org/licenses/>.

import os
import re
import string

from subprocess import call
from subprocess import check_output

import libs.ConfigLoader as ConfigLoader

from libs.Tools import Tools

config = ConfigLoader.GetConfigModule()

class Scanner(object):
    _bootKernels = []
    _fstabValues = []
    _driveLayout = ""

    # Kernels defined by user in configuration file (Example: Gentoo, 3.14.27-KS.01, vmlinuz, initrd, root=/dev/sda1)
    _configKernelLabel = []
    _configKernelVersion = []
    _configKernelDefault = []
    _configKernelName = []
    _configKernelInitrdName = []
    _configKernelOptions = []

    # Factorized Kernels List (The kernels that were found in the 'kernelDirectory' and defined by user in the config)
    _commonKernels = []

    @classmethod
    def __init__(cls):
        # Get the fstab values for /boot immediately
        cls.ScanFstab()

        # boot drive
        cls._bootDriveField = cls._fstabValues[0]
        cls._bootDrive = Tools.MapIdentifierToDrive(cls._bootDriveField)

        # Detect the layout of the /boot drive
        cls.DetectDriveLayout()

    # Finds the kernels that the user has in their 'kernelDirectory'
    @classmethod
    def FindBootKernels(cls):
        Tools.Print("Scanning " + config.kernelDirectory + " ...")

        # Check to see if our boot directory exists before starting
        if not os.path.exists(config.kernelDirectory):
            Tools.Print("The " + config.kernelDirectory + " directory doesn't exist. Creating ...")

            os.mkdir(config.kernelDirectory)

            if os.path.exists(config.kernelDirectory):
                Tools.Warn("Please place your kernels inside " + config.kernelDirectory + "/<version>, configure " +
                    ConfigLoader.GetConfigFilePath() + ", and then re-run the program. \n\nExample:\n\n" +
                    config.kernelDirectory + "/3.12.12-KS.01/{vmlinuz, initrd}")
                quit(1)
            else:
                Tools.Fail(config.kernelDirectory + " directory doesn't exist")

        cmd = 'ls ' + config.kernelDirectory
        results = check_output(["ls", config.kernelDirectory], universal_newlines=True).strip()

        # Add kernels to out kernel set
        if results:
            for i in results.split("\n"):
                cls._bootKernels.append(i)
        else:
            Tools.Fail("No kernels found in " + config.kernelDirectory + ". A directory for each kernel you want must exist " +
            "in that location.\n\nExample:\n\n" + config.kernelDirectory + "/3.13.5-KS.01/\n" + config.kernelDirectory + "/3.14.27-KS.01/\n")

    # Get fstab information. We will use this to get /boot
    @classmethod
    def ScanFstab(cls):
        cmd = 'cat /etc/fstab | grep /boot[[:blank:]] | awk \'{print $1, $2, $3, $4, $5, $6}\''
        results = check_output(cmd, shell=True, universal_newlines=True).strip()

        if results:
            # Split the /boot line so we can store it
            splits = results.split(" ")

            # Save fstab /boot drive info
            for x in splits:
                cls._fstabValues.append(x.strip())
        else:
            Tools.Fail("/boot line could not be found in /etc/fstab")

    # Detect the partition style for the /boot drive (gpt or mbr) and returns either "gpt" or "msdos" as a string
    @classmethod
    def DetectDriveLayout(cls):
        # If we are using 'whole disk zfs', we know for a fact that
        # it's gpt (assuming the drive was formatted with zpool create).

        # However, if the person partitioned the drive manually and is
        # still using the whole drive for zfs (technically speaking),
        # then they could be using mbr as well.. returning 'none' so that
        # both part_<> can be included
        if config.wholeDiskZfs:
            cls._driveLayout = "none"
        else:
            # Remove the partition number so that we can find the
            # style of the drive itself
            match = re.sub("\d$", "", cls._bootDrive)

            if match:
                # use blkid /dev/<drive> and get PTTYPE
                # example: blkid /dev/vda: -> /dev/vda: PTTYPE="gpt"
                # cmd: blkid /dev/sda | grep -oE 'PTTYPE=".*"' | cut -d '"' -f 2
                cmd = 'blkid ' + match.strip() + ' | grep -oE \'PTTYPE=".*"\' | cut -d \'"\' -f 2'
                results = check_output(cmd, shell=True, universal_newlines=True).strip()

                if results:
                    if results == "gpt":
                        cls._driveLayout = "gpt"
                    elif results == "dos":
                        cls._driveLayout = "msdos"
                    else:
                        cls._driveLayout = "none"
                else:
                    # This will run if we get some weird result like "md" from "/dev/md0"
                    cls._driveLayout = "none"
            else:
                # If the layout couldn't be detected then return none so that both msdos/gpt can be inserted.
                # This will happen if the user has a raid or lvm device as their /boot.
                cls._driveLayout = "none"

    # Converts the fstab /boot drive entry to a grub 2 compatible format
    # and returns it as a string: (gpt) /dev/sda1 -> (hd0,gpt1)
    @classmethod
    def GetGrub2BootDrive(cls):
        # If we are using 'whole disk zfs', then we won't have a /boot entry
        # in /etc/fstab. So instead we will format the zfs_boot variable and
        # return it ready to be used in grub2
        if config.wholeDiskZfs:
            match = re.search('(/[a-zA-Z0-9_/]+)', config.wholeDiskZfsBootPool)

            if match:
                return match.group()

            Tools.Fail("Could not parse the 'wholeDiskZfsBootPool' variable correctly.")

        # Properly processes the boot drive field in order for us to get
        # a value that we can properly parse for the grub.cfg.
        # This is so that if the user is using UUIDs as a /boot entry in
        # /etc/fstab, we can handle that situation correctly.
        match = re.search('/dev/(.*)', cls._bootDrive)

        if match:
            # Possibilities:
            # sd[a-z][0+]
            # vd[a-z][0+]
            # md[0+]
            # mapper/vg-root
            # vg/root

            # --- Handle sdX or vdX drives ---
            m1 = re.search('[s|v]d(\w+)', match.group(1))

            if m1:
                # Complete value, will be completed as function progresses
                completedValue = "(hd"

                # Process the letter part and convert it to a grub compatible format; a = (hd0)
                alph = re.search('\w', m1.group(1))

                if alph:
                    # Find the number in the alphabet of this letter
                    alphindex = cls.GetAlphabeticalIndex(alph.group(0))

                    # Add this number to the final string
                    completedValue = completedValue + str(alphindex)

                # Process the number part of the drive
                numberPartOfDrive = re.search('\d', m1.group(1))

                if numberPartOfDrive:
                    # add layout
                    completedValue = completedValue + "," + cls._driveLayout

                    # add number part
                    completedValue = completedValue + numberPartOfDrive.group(0)

                # close the value and return it
                completedValue = completedValue + ")"

                return completedValue

            # --- Handle md# ---
            m1 = re.search('md(\d+)', match.group(1))

            if m1:
                return "(md/" + m1.group(1) + ")"

            # --- LVM: mapper/<volume_group>-<logical_volume> ---
            m1 = re.search('mapper/(\w.-\w+)', match.group(1))

            if m1:
                return "(lvm/" + m1.group(1) + ")"

            # --- LVM: <volume_group>/<logical_volume> ---
            m1 = re.search('(\w+)/(\w+)', match.group(1))

            if m1:
                return "(lvm/" + m1.group(1) + "-" + m1.group(2) + ")"

            # We've failed :(
            Tools.Fail("Unable to generate the boot drive entry.")

    # Returns the kernel set that was gathered
    @classmethod
    def GetBootKernels(cls):
        return cls._bootKernels

    # Prints a list of detected kernels in the boot directory
    @classmethod
    def PrintBootKernels(cls):
        Tools.Print("Kernels detected in the " + config.kernelDirectory + " directory:")

        for kernel in cls._bootKernels:
            Tools.Print(kernel)

    # Finds the kernels that the user defined in their configuration file
    @classmethod
    def FindKernelsInConfig(cls):
        Tools.Print("Scanning " + ConfigLoader.GetConfigFilePath() + " ...")

        for kernel in config.kernels:
            cls._configKernelLabel.append(kernel[0])
            cls._configKernelVersion.append(kernel[1])
            cls._configKernelDefault.append(kernel[2])
            cls._configKernelName.append(kernel[3])
            cls._configKernelInitrdName.append(kernel[4])
            cls._configKernelOptions.append(kernel[5])

    # Prints the kernels detected in the configuration file
    @classmethod
    def PrintKernelsInConfig(cls):
        Tools.Print("Kernels detected in " + ConfigLoader.GetConfigFilePath() + ":")

        for i in range(len(cls._configKernelLabel)):
            print(str(i+1) + ". " + cls._configKernelLabel[i] + " - " + cls._configKernelVersion[i])

    # Factors out the kernels that were defined by the user and found in their kernelDirectory
    @classmethod
    def FindCommonKernels(cls):
         for i in range(len(cls._bootKernels)):
            for j in range(len(cls._configKernelVersion)):
                if cls._bootKernels[i] == cls._configKernelVersion[j]:
                    value = [
                        cls._configKernelLabel[j],
                        cls._configKernelVersion[j],
                        cls._configKernelDefault[j],
                        cls._configKernelName[j],
                        cls._configKernelInitrdName[j],
                        cls._configKernelOptions[j],
                    ]
                    cls._commonKernels.append(value)

    # Finds the default kernel
    @classmethod
    def FindDefaultKernel(cls):
        alreadyFound = 0
        defaultKernelIndex = 0

        for i in range(len(cls._commonKernels)):
            if cls._commonKernels[i][2] == 1:
                if alreadyFound == 0:
                    alreadyFound = 1
                    defaultKernelIndex = i
                else:
                    Tools.Warn("Multiple default kernels detected. The default kernel will most likely not be correct!")
                    return defaultKernelIndex

        if alreadyFound != 0:
            return defaultKernelIndex
        else:
            return -1

    # Gets the common kernel list
    @classmethod
    def GetCommonKernels(cls):
        return cls._commonKernels

    # Prints the kernels found in common
    @classmethod
    def PrintCommonKernels(cls):
        Tools.Print("Common kernels detected:")

        for kernel in range(len(cls._commonKernels)):
            print(str(kernel+1) + ". " + cls._commonKernels[kernel][0] + " - " + cls._commonKernels[kernel][1])

    # Returns the index for target kernel in the common kernel list
    @classmethod
    def GetKernelIndexInCommonList(cls, vTarget):
        for i in range(len(cls._commonKernels)):
            if cls._commonKernels[i] == vTarget:
                return i

        return -1

    # Retrieves the kernel from the common list
    @classmethod
    def GetKernel(cls, vTarget):
        return cls._commonKernels[vTarget]

    # Checks to see if any kernels will be added to the configuration file
    @classmethod
    def AnyKernelsExist(cls):
        if not cls._commonKernels:
            return -1
        else:
            return 0

    # Gets the layout that was detected
    @classmethod
    def GetDriveLayout(cls):
        return cls._driveLayout

    # Get the index for a letter in the alphabet
    @classmethod
    def GetAlphabeticalIndex(cls, vLetter):
        alphabet = string.ascii_lowercase

        count = 0

        for letter in alphabet:
            if letter == vLetter:
                return count

            count = count + 1
