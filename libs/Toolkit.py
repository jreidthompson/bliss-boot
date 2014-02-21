# Copyright (C) 2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import string

from etc import conf

class Toolkit(object):
        # Creates a symlink in /boot that points back to itself
        def create_bootlink(self):
                if not os.path.exists("/boot/boot"):
                        os.chdir("/boot")
                        os.symlink(".", "boot")

        # Cleanly exit the application
        def die(self, message):
                print("[Error] " + message + ". Exiting ...")

                # Remove the incomplete bootloader file
                if conf.bootloader == "grub2":
                        if os.path.exists("grub.cfg"):
                                os.remove("grub.cfg")
                elif conf.bootloader == "extlinux":
                        if os.path.exists("extlinux.conf"):
                                os.remove("extlinux.conf")

                quit(5)

        # Get the index for a letter in the alphabet
        def get_alph_index(self, letter):
                alphabet = string.ascii_lowercase

                count = 0

                for let in alphabet:
                        if let == letter:
                                return count

                        count = count + 1

        # Find values in common from two lists and return a third list
        def find_common_kernels(self, list_a, list_b):
           common_list = []

           for a in list_a:
                for b in list_b:
                    if a == b:
                        print("Commonality found: " + a + " " + b)
                    common.list.append(a)

             return common_list

                
