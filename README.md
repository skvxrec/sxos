# sxOS
*you will KISS this distro*

Gentoo-based distro with clang, musl, OpenRC and a simple installer.

## features
- clang as the only compiler
- musl libc
- OpenRC init
- simple installer (installsx.py) — installs doas and GRUB by default

## planned
- custom kernel (BFQ, KSM patches)
- custom stage3 (clang + doas preinstalled)

## install
```
python3 installsx.py
```

## based on
Gentoo Linux
