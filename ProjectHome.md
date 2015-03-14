This script attempts to provide an automatic way to convert a syslinux configuration file in one which can be used with GRUB legacy and grub4dos.

The software converts submenus correctly and warns the user in case of unknown entries.

It is possible to specify that the output menu should go into `/foo/bar.lst` with respect to the root of the disk. In this case, entries in the original file are prefixed with the correct path. For example `/vmlinuz` becomes `/foo/vmlinuz`.

This is useful if one wants to unpack a disk image (like an ISO file) and put all the contents in a subdirectory of a new disk image, thus allowing the inclusion of multiple bootable disks in one (multi-boot).

Quick link to the source:

http://code.google.com/p/syslinux2menulst/source/browse/trunk/syslinux2menulst.py