# syslinux2menulst

This script attempts to provide an automatic way to convert a syslinux configuration file in one which can be used with GRUB legacy and grub4dos.

The software converts submenus correctly and warns the user in case of unknown entries.

It is possible to specify that the output menu should go into `/foo/bar.lst` with respect to the root of the disk. In this case, entries in the original file are prefixed with the correct path. For example `/vmlinuz` becomes `/foo/vmlinuz`.

This is useful if one wants to unpack a disk image (like an ISO file) and put all the contents in a subdirectory of a new disk image, thus allowing the inclusion of multiple bootable disks in one (multi-boot).

```
$ syslinux2menulst.py -h
usage: syslinux2menulst.py [-h] FILE PATH DIRECTORY

Convert a syslinux/isolinux file to a GRUB menu.lst.

positional arguments:
  FILE        Input file
  PATH        Absolute path in the disk structure, e.g. /menu.lst
  DIRECTORY   Output root directory (will be created if not present)

optional arguments:
  -h, --help  show this help message and exit
```
