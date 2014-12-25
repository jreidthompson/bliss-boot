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

from libs.Toolkit import Toolkit as tools
from libs.Scanner import Scanner
from libs.Installer import Installer
from libs.ConfigLoader import ConfigLoader

import libs.Variables as var

scanner = Scanner()

config = ConfigLoader.get_config()

class Manager(object):
    def __init__(self):
        # Find all the kernels in the user's boot directory (config.bootdir)
        scanner.find_boot_kernels()

        # Find all the kernels that the user configured in their configuration file
        scanner.find_config_kernels()

        # Find all the kernels that were found in their boot directory and where a definition was found in their configuration file
        scanner.factor_common_kernels()

        # Checks to see that at least one kernel entry will be written
        result = scanner.any_kernels()

        if result == -1:
            tools.die("Please add your desired kernels and their options to the 'kernels' list in " +
            ConfigLoader.get_config_file() + ".\n" + "These entries should match the kernels you have in " +
            config.bootdir + ".")

        # Get /boot drive layout
        self.layout = scanner.get_layout()

    # Generates the bootloader configuration
    def write_entries(self):
        output_file = ""

        is_output = tools.is_output()

        if is_output:
            output_file = tools.get_output_file()

            # Check to see if the directory for this file exists. If it doesn't
            # create any directories leading up to the output file so that we don't
            # get a "FileNotFoundError" later on
            output_parent = os.path.dirname(output_file)

            if not os.path.exists(output_parent):
                self.create_output_dir(output_parent)

        elif not is_output and config.bootloader == "grub2":
            output_file = "grub.cfg"
        elif not is_output and config.bootloader == "extlinux":
            output_file = "extlinux.conf"

        # Check to see what's the bootloader before we start adding
        # all the entries, depending the bootloader we can cleanly start
        # adding generic information like default kernel, timeouts, etc
        position = scanner.search(config.default)

        if position != -1:
            if config.bootloader == "grub2":
                tools.eprint("Generating GRUB 2 configuration ...")

                bootdrive = scanner.get_grub2_bootdrive()

                if os.path.exists(output_file):
                    if tools.is_force():
                        dossier = open(output_file, "w")
                    else:
                        tools.die("Target file: " + output_file + " already exists. Pass -f to overwrite.")
                else:
                    dossier = open(output_file, "w")

                dossier.write("set timeout=" + str(config.timeout) + "\n")
                dossier.write("set default=" + str(position) + "\n")
                dossier.write("\n")

                # Write the modules that need to be inserted depending
                # drive style. For whole disk zfs, none will be returned
                # since a person can partition the drive manually and use msdos,
                # or they can let zfs format their drive automatically with
                # gpt. This ambiguity will be the reason both grub modules will
                # be inserted.

                if self.layout == "gpt":
                    dossier.write("insmod part_gpt\n")
                elif self.layout == "msdos":
                    dossier.write("insmod part_msdos\n")
                elif self.layout == "none":
                    dossier.write("insmod part_gpt\n")
                    dossier.write("insmod part_msdos\n")

                if config.efi:
                    dossier.write("insmod efi_gop\n")
                    dossier.write("insmod efi_uga\n")
                    dossier.write("insmod fat\n")

                if config.zfs:
                    dossier.write("insmod zfs\n")

                if config.goody_bag:
                    for candy in config.goody_bag:
                        dossier.write("insmod " + candy + "\n")

                if not config.zfs:
                    dossier.write("\nset root='" + bootdrive + "'\n")

                dossier.write("\n")
                dossier.close()
            elif config.bootloader == "extlinux":
                tools.eprint("Generating extlinux configuration ...")

                # Gets the name of the default kernel
                dk_name = scanner.get_kernel(position)[0]

                if os.path.exists(output_file):
                    if tools.is_force():
                        dossier = open(output_file, "w")
                    else:
                        tools.die("Target file: " + output_file + " already exists. Pass -f to overwrite.")
                else:
                    dossier = open(output_file, "w")

                dossier.write("TIMEOUT " + str(int(config.timeout * 10)) + "\n")

                if not config.el_auto_boot:
                    dossier.write("UI " + config.el_ui + "\n")

                dossier.write("\n")
                dossier.write("DEFAULT " + dk_name + str(position) + "\n\n")
                dossier.write("MENU TITLE " + config.el_m_title + "\n")
                dossier.write("MENU COLOR title " + config.el_c_title + "\n")
                dossier.write("MENU COLOR border " + config.el_c_border + "\n")
                dossier.write("MENU COLOR unsel " + config.el_c_unsel + "\n")
                dossier.write("\n")
                dossier.close()
            else:
                tools.die("The bootloader defined in " + ConfigLoader.get_config_file() + " is not supported.")
        else:
            tools.die("The default kernel entry in " + ConfigLoader.get_config_file() + " was not found in " + config.bootdir)

        # Add all our desired kernels
        for kernel in scanner.get_common_kernels():
            # Get the position so that we can create the labels correctly
            position = scanner.search(kernel[1])

            tools.esucc("Adding: " + kernel[0] + " - " + kernel[1])

            cs = self.strip_head(config.bootdir)
            full_kernel_path = cs + "/" + kernel[1]

            # Depending the bootloader we have specified, generate
            # its appropriate configuration.
            if config.bootloader == "grub2":
                # Open it in append mode since the header was previously
                # created before.
                dossier = open(output_file, "a")
                dossier.write("menuentry \"" + kernel[0] + " - " + kernel[1] + "\" {\n")

                if config.zfs:
                    dossier.write("\tlinux " + bootdrive + "/@" + full_kernel_path + "/" + config.kernel_prefix + " " + kernel[2] + "\n")

                    if config.initrd:
                        dossier.write("\tinitrd " + bootdrive + "/@" + full_kernel_path + "/" + config.initrd_prefix + "\n")

                else:
                    dossier.write("\tlinux " + full_kernel_path + "/" + config.kernel_prefix + " " + kernel[2] + "\n")

                    if config.initrd:
                        dossier.write("\tinitrd " + full_kernel_path + "/" + config.initrd_prefix + "\n")

                dossier.write("}\n\n")
                dossier.close()
            elif config.bootloader == "extlinux":
                dossier = open(output_file, "a")
                dossier.write("LABEL " + kernel[0] + str(position) + "\n")
                dossier.write("\tMENU LABEL " + kernel[0] + " - " + kernel[1] + "\n")
                dossier.write("\tLINUX " + full_kernel_path + "/" + config.kernel_prefix + "\n")

                if config.initrd:
                    dossier.write("\tINITRD " + full_kernel_path + "/" + config.initrd_prefix + "\n")

                dossier.write("\tAPPEND " + kernel[2] + "\n")
                dossier.write("\n")
                dossier.close()

        # Append anything else the user wants automatically added
        if config.append and config.append_stuff:
            tools.eprint("Appending additional information ...")

            if config.bootloader == "grub2":
                dossier = open(output_file, "a")
                dossier.write(config.append_stuff)
                dossier.close()
            elif config.bootloader == "extlinux":
                dossier = open(output_file, "a")
                dossier.write(config.append_stuff)
                dossier.close()

        # Check to make sure that the file was created successfully.
        # If so let the user know..
        if os.path.isfile(output_file):
            tools.esucc("'" + output_file + "' has been created!")
        else:
            tools.die("Either the file couldn't be created or the specified bootloader isn't supported.")

    # Triggers bootloader installation
    def install_bootloader(self):
        # Set the drive using the /boot entry in /etc/fstab if the user wants
        # to install a bootloader but didn't specify the drive themselves as an argument.
        if not tools.get_bl_drive():
            installer = Installer(scanner.get_bootdrive())
        else:
            installer = Installer(tools.get_bl_drive())

        # Set extlinux specific information before we start
        if installer.get_bootloader() == "extlinux":
            installer.set_drive_number(scanner.get_bootdrive_num())
            installer.set_drive_type(scanner.get_layout())

        installer.start()

    # Strips the first directory of the path passed. Used to get a good path and not need
    # a boot symlink in /boot
    def strip_head(self, path):
        if path:
            splinters = path.split("/")
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
            tools.die("The value to strip is empty ...")

    # Creates all the directories needed so that the output file can be written
    def create_output_dir(self, parent_dir):
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

            if not os.path.exists(parent_dir):
                tools.die("Unable to create the " + parent_dir + " directory ...")
