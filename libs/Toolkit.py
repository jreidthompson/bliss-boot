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
import sys

from subprocess import call
from subprocess import check_output

import libs.Variables as var

# Provides basic utilities that can be used by any class (Colorized printing, parameter retrieval, etc)
class Toolkit(object):
    args_force = 0
    args_output = ""
    bl_drive = ""
    bl_extlinux = 0
    bl_el_path = "/boot/extlinux"
    bl_grub2 = 0
    bl_only = 0

    args_options = (
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
    def is_flag(cls, candidate):
        for i in range(len(cls.args_options)):
            for j in range(len(cls.args_options[i])):
                if cls.args_options[i][j] == candidate:
                        return 0

        return -1

    # Checks parameters and running user
    @classmethod
    def welcome(cls):
        user = check_output(["whoami"], universal_newlines=True).strip()

        if user != "root":
            cls.die("This program must be ran as root")

        arguments = sys.argv[1:]

        if len(arguments) >= 1:
            for i in range(len(arguments)):
                # Sets the output file to write the config to
                if arguments[i] == "-o" or arguments[i] == "--output":
                    try:
                        if cls.is_flag(arguments[i+1]) != 0:
                            cls.args_output = arguments[i+1]
                    except IndexError:
                        cls.die("You need to pass a path to output the file!")

                # Set 'force' in order to overwrite output file target
                elif arguments[i] == "-f" or arguments[i] == "--force":
                    cls.args_force = 1

                # Set the drive where we want to install the bootloader
                elif arguments[i] == "-d" or arguments[i] == "--drive":
                    try:
                        if cls.is_flag(arguments[i+1]) != 0:
                            cls.bl_drive = arguments[i+1]
                    except IndexError:
                        pass

                # Let the program know that we want to install extlinux
                elif arguments[i] == "-E" or arguments[i] == "--install-extlinux":
                    cls.bl_extlinux = 1

                    try:
                        if cls.is_flag(arguments[i+1]) != 0:
                            cls.bl_el_path = arguments[i+1]
                    except IndexError:
                        pass

                # Let the program know that we want to install GRUB 2
                elif arguments[i] == "-G" or arguments[i] == "--install-grub2":
                    cls.bl_grub2 = 1

                # Displays the help/usage message
                elif arguments[i] == "-h" or arguments[i] == "--help":
                    cls.print_usage()

                # Sets the tasks to do (bootloader|config only, or both)
                elif arguments[i] == "-B" or arguments[i] == "--only-bootloader":
                    cls.bl_only = 1

    # Prints the header of the application
    @classmethod
    def PrintHeader(cls):
        cls.Print(cls.Colorize("yellow", "----------------------------------"))
        cls.Print(cls.Colorize("yellow", var.name + " - v" + var.version))
        cls.Print(cls.Colorize("yellow", var.contact))
        cls.Print(cls.Colorize("yellow", "Distributed under the " + var.license))
        cls.Print(cls.Colorize("yellow", "----------------------------------") + "\n")

    # Prints the usage information
    @staticmethod
    def print_usage():
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
    def die(cls, message):
        call(["echo", "-e", cls.colorize("red", message)])
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
    def eprint(cls, message):
        call(["echo", "-e", cls.Colorize("cyan", message)])

    # Prints a message
    @classmethod
    def Print(cls, message):
        call(["echo", "-e", cls.Colorize("cyan", message)])

    # Used for successful entries
    @classmethod
    def esucc(cls, message):
        call(["echo", "-e", cls.Colorize("green", message)])

    # Used for warnings
    @classmethod
    def ewarn(cls, message):
        call(["echo", "-e", cls.Colorize("yellow", message)])

    # Returns the value of whether or not GRUB 2 will be installed
    @classmethod
    def is_grub2(cls):
        return cls.bl_grub2

    # Returns the value of whether or not extlinux will be installed
    @classmethod
    def is_extlinux(cls):
        return cls.bl_extlinux

    # Returns a positive number if an output option was set
    @classmethod
    def is_output(cls):
        if cls.args_output:
            return 1

        return 0

    # Gets the desired output path
    @classmethod
    def get_output_file(cls):
        return cls.args_output

    # Returns the value of whether or not we will overwrite the output file if it exists.
    @classmethod
    def is_force(cls):
        return cls.args_force

    # Returns extlinux variables
    @classmethod
    def get_el_path(cls):
        return cls.bl_el_path

    # Sets the bootloader drive
    @classmethod
    def set_bl_drive(cls, drive):
        cls.bl_drive = drive

    # Returns the bootloader drive
    @classmethod
    def get_bl_drive(cls):
        return cls.bl_drive

    # Returns if we are only going to install the bootloader
    @classmethod
    def only_bootloader(cls):
        return cls.bl_only

