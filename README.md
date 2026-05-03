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

## stages

**stage1** — base system with a broken clang (not usable as a compiler)

**stage2** — gcc, make, git, python, doas, sxpkg (package manager). This is the recommended starting point.

## install
Download the latest stage from [releases](https://github.com/skvxrec/sxos/releases). Stage2 is recommended.

Boot any live ISO (e.g. Arch Linux), then extract the stage, set up GRUB and the kernel manually like LFS. There is no sxOS ISO yet — use whatever live environment you have.

Automated installer is planned but not ready yet.

## built
From scratch
