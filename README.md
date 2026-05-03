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

Boot any live ISO (e.g. Arch Linux), extract the stage to your partition, chroot into it and install the kernel and bootloader:

```sh
sxpkg install linux
sxpkg install grub
```

Then:

```sh
# UEFI
mount /dev/nvmeXnXpX /boot/efi
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=sxOS

# BIOS
grub-install /dev/sdX

# create /boot/grub/grub.cfg manually (grub-mkconfig is not supported yet)
mkdir -p /boot/grub
cat > /boot/grub/grub.cfg << EOF
set default=0
set timeout=5

menuentry "sxOS" {
    set root=(hd0,1)
    linux /boot/vmlinuz root=/dev/sda1 rw
}
EOF
```

Adjust `(hd0,1)` and `root=/dev/sda1` to match your partition.

Don't forget to set a root password before rebooting, otherwise the system will drop into an emergency shell:

```sh
passwd root
```

Automated installer is planned but not ready yet.

## built
From scratch
