# Copyright 2014-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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

    _options = (
        ("-o", "--output"),
        ("-f", "--force"),
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

                # Displays the help/usage message
                elif arguments[i] == "-h" or arguments[i] == "--help":
                    cls.PrintUsage()

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
