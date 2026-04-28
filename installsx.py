#!/usr/bin/env python3
import subprocess
import os
import sys
import getpass

STAGE3_URL = "https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-musl-openrc/"
MOUNT = "/mnt/gentoo"

def run(cmd, check=True):
    subprocess.run(cmd, shell=True, check=check)

def chroot(cmd):
    subprocess.run(["chroot", MOUNT, "/bin/bash", "-c", cmd], check=True)

def ask(prompt):
    return input(prompt).strip()

def main():
    if os.geteuid() != 0:
        print("run as root")
        sys.exit(1)

    print("=== sxOS installer ===\n")

    # disk
    disk = ask("disk (e.g. /dev/sda or /dev/nvme0n1): ")
    run(f"cfdisk {disk}")

    boot_part = ask("boot partition (e.g. /dev/sda1): ")
    root_part = ask("root partition (e.g. /dev/sda2): ")

    # format
    run(f"mkfs.fat -F32 {boot_part}")
    run(f"mkfs.ext4 {root_part}")

    # mount
    run(f"mount {root_part} {MOUNT}")
    run(f"mkdir -p {MOUNT}/boot")
    run(f"mount {boot_part} {MOUNT}/boot")

    # user info
    root_pass = getpass.getpass("root password: ")
    root_pass2 = getpass.getpass("confirm root password: ")
    if root_pass != root_pass2:
        print("passwords don't match")
        sys.exit(1)

    username = ask("username: ")
    doas_access = ask(f"give {username} doas access? [y/n]: ").lower() == 'y'
    jobs = ask("cpu cores (for -j): ")
    opt = ask("optimization [2/3]: ")

    # stage3
    print("\ndownloading stage3...")
    run(f"wget -q -O /tmp/stage3list {STAGE3_URL}")
    import re
    with open("/tmp/stage3list") as f:
        content = f.read()
    match = re.search(r'(stage3-amd64-musl-openrc-\d+T\d+Z\.tar\.xz)', content)
    if not match:
        print("could not find stage3 filename")
        sys.exit(1)
    stage3_name = match.group(1)
    run(f"wget -O {MOUNT}/stage3.tar.xz {STAGE3_URL}{stage3_name}")
    run(f"tar xpvf {MOUNT}/stage3.tar.xz --xattrs-include='*.*' --numeric-owner -C {MOUNT}")
    run(f"rm {MOUNT}/stage3.tar.xz")

    # make.conf
    make_conf = f"""COMMON_FLAGS="-O{opt} -pipe"
CFLAGS="${{COMMON_FLAGS}}"
CXXFLAGS="${{COMMON_FLAGS}}"
CHOST="x86_64-pc-linux-musl"
MAKEOPTS="-j{jobs}"
CC=clang
CXX=clang++
AR=llvm-ar
NM=llvm-nm
RANLIB=llvm-ranlib
USE="openrc"
"""
    with open(f"{MOUNT}/etc/portage/make.conf", "w") as f:
        f.write(make_conf)

    # chroot prep
    run(f"cp /etc/resolv.conf {MOUNT}/etc/resolv.conf")
    run(f"mount -t proc /proc {MOUNT}/proc")
    run(f"mount --rbind /sys {MOUNT}/sys")
    run(f"mount --rbind /dev {MOUNT}/dev")

    # sync portage
    chroot("emerge-webrsync")

    # install clang + grub
    chroot("emerge --ask=n sys-devel/clang sys-boot/grub app-admin/doas")

    # grub
    chroot("grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=sxOS")
    chroot("grub-mkconfig -o /boot/grub/grub.cfg")

    # root password
    subprocess.run(f"echo 'root:{root_pass}' | chroot {MOUNT} chpasswd", shell=True, check=True)

    # user
    chroot(f"useradd -m -G wheel,audio,video,usb {username}")
    user_pass = getpass.getpass(f"password for {username}: ")
    subprocess.run(f"echo '{username}:{user_pass}' | chroot {MOUNT} chpasswd", shell=True, check=True)

    # doas
    if doas_access:
        with open(f"{MOUNT}/etc/doas.conf", "w") as f:
            f.write(f"permit {username} as root\n")

    # hostname
    hostname = ask("hostname: ")
    with open(f"{MOUNT}/etc/hostname", "w") as f:
        f.write(hostname + "\n")

    # openrc
    chroot("rc-update add NetworkManager default")

    print("\ndone. reboot and remove install media.")

if __name__ == "__main__":
    main()
