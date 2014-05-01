# Copyright 2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class Installer:
	# Installs GRUB 2
	def install_grub2(self, drive):
		self.eprint("Installing GRUB 2 to " + drive + " ...")

		result = call(["grub-install", drive])

		if result == 0:
			self.esucc("GRUB 2 Installed Successfully!")
		elif result != 0:
			self.die("Failed to install GRUB 2 into " + drive)

	# Installs Extlinux
	def install_extlinux(self, path, drive, dnum, mtype):
		self.eprint("Installing extlinux to " + path + " and writing firmware to " + drive + " ...")

		# First make the directory to install extlinux in
		if not os.path.exists(path):
			os.makedirs(path)

			if not os.path.exists(path):
				self.die("Unable to create the " + path + " directory ...")

		# Install extlinux to folder
		result = call(["extlinux", "--install", path])

		if result == 0:
			self.esucc("Extlinux was installed successfully to " + path + "!")
		elif result != 0:
			self.die("Failed to install extlinux into " + path)

		# Copy menu.c32 and libutil.c32
		el_files = [
			"/usr/share/syslinux/menu.c32",
			"/usr/share/syslinux/libutil.c32"
		]

		for i in el_files:
			if os.path.isfile(i):
				shutil.copy(i, path)

				if not os.path.isfile(path + "/" + os.path.basename(i)):
					self.die("Failed to copy " + os.path.basename(i) + "!") 
			else:
				self.die(os.path.basename(i) + " doesn't exist")

		# GPT
		if mtype == "gpt":
			firm = "/usr/share/syslinux/gptmbr.bin"

			# Toggle GPT bios bootable flag
			cmd = "sgdisk " + drive + " --attributes=" + dnum + ":set:2"
			result = call(cmd, shell=True)
			
			if result == 0:
				self.esucc("Succesfully toggled legacy bios bootable flag!")
				cmd = "sgdisk " + drive + " --attributes=" + dnum + ":show"
				result = call(cmd, shell=True)
			elif result != 0:
				self.die("Error setting legacy bios bootable flag!")
		# MBR
		elif mtype == "msdos":
			firm = "/usr/share/syslinux/mbr.bin"

		# Write the firmware to the drive
		if mtype == "gpt" or mtype == "msdos":
			if os.path.isfile(firm):
				self.eprint("Writing firmware to " + drive + " ...")

				cmd = "dd bs=440 conv=notrunc count=1 if=" + firm + " of=" + drive
				result = call(cmd, shell=True)

				if result == 0:
					self.esucc(os.path.basename(firm) + " was successfully written to " + drive + "!")
				elif result != 0:
					self.die("Failed to write extlinux firmware to " + drive + "!")
		else:
			self.die("Unable to determine firmware to use for extlinux ...")

	# Gets and sets the parameters retrieved from the parameters
	def set_args(self, atool):
		self.args_force = atool.get_args_force()
		self.args_output = atool.get_args_output()
		self.boot_install = atool.get_boot_install()
		self.args_el_path = atool.get_el_path()
	
	# Installs the bootloader
	def install_bootloader(self):
		# What bootloader are we going to install?
		bootl = self.boot_install

		# Run this so we can set the layout that we need
		bootdrive = scanner.get_bootdrive()

		if bootl == 1:
			tools.install_grub2(bootdrive)
		elif bootl == 2:
			bootdrive_num = scanner.get_bootdrive_num()

			if bootdrive_num != -1:
				tools.install_extlinux(self.args_el_path, bootdrive, bootdrive_num, self.layout)
