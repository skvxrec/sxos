# sxOS
*suffering from source*

Distro built from scratch with a custom package manager and a simple installer.

## features
- gcc as the system compiler
- OpenRC init
- simple installer on Python (installsx.py)
- custom package manager inspired by KISS Linux (sxpkg)
- doas instead of sudo

## planned
- bootable ISO (WIP, not working yet)
- custom kernel (BFQ, KSM patches)
- musl version
- custom init based on sinit

## install
Installation is done manually like LFS — download the stage, then set up GRUB, Linux kernel, and other system components by hand, as they are not yet in the package manager.

Automated installer is planned but not ready yet.

## built
From scratch
