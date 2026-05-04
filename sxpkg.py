#!/usr/bin/env python3
import subprocess
import os
import sys
import shutil

REPO = os.path.expanduser("~/.sxpkg/repo")
REPO_URL = "https://github.com/skvxrec/sxpkg-repo"
ROOT = os.environ.get("SXROOT", "")
DB = ROOT + "/var/lib/sxpkg"
BUILD_DIR = "/tmp/sxpkg-build"

def run(cmd, cwd=None):
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def download(url, dest):
    if shutil.which("curl"):
        run(f"curl -fsSLk -o {dest} {url}")
    elif shutil.which("wget"):
        run(f"wget --no-check-certificate -O {dest} {url}")
    else:
        print("error: no downloader found (need curl or wget)")
        sys.exit(1)

def installed(pkg):
    return os.path.exists(f"{DB}/{pkg}")

def install(pkg, visited=None):
    if visited is None:
        visited = set()
    if pkg in visited:
        return
    visited.add(pkg)

    if installed(pkg):
        print(f"==> {pkg} already installed")
        return

    pkg_dir = f"{REPO}/{pkg}"
    if not os.path.exists(pkg_dir):
        print(f"error: package '{pkg}' not found in repo")
        sys.exit(1)

    depends = f"{pkg_dir}/depends"
    if os.path.exists(depends):
        with open(depends) as f:
            for dep in f.read().splitlines():
                dep = dep.strip()
                if dep:
                    install(dep, visited)

    print(f"==> installing {pkg}")
    work = f"{BUILD_DIR}/{pkg}"
    os.makedirs(work, exist_ok=True)

    with open(f"{pkg_dir}/sources") as f:
        for url in f.read().splitlines():
            url = url.strip()
            if url:
                filename = url.split('/')[-1]
                if not os.path.exists(f"{work}/{filename}"):
                    download(url, f"{work}/{filename}")

    for f in os.listdir(work):
        if f.endswith((".tar.gz", ".tar.xz", ".tar.bz2", ".tar.zst")):
            run(f"tar xf {work}/{f} -C {work}")
        elif f.endswith(".zip"):
            run(f"unzip -o {work}/{f} -d {work}")

    subdirs = [d for d in os.listdir(work) if os.path.isdir(f"{work}/{d}")]
    src = f"{work}/{subdirs[0]}" if subdirs else work

    dest = f"{DB}/{pkg}"
    os.makedirs(dest, exist_ok=True)
    run(f"cd {src} && sh {pkg_dir}/build {dest}")

    files = []
    for root, dirs, filenames in os.walk(dest):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            system_path = "/" + os.path.relpath(filepath, dest)
            files.append(system_path)

    run(f"cp -r {dest}/. {ROOT}/")
    run(f"ldconfig {ROOT}/usr/lib {ROOT}/lib {ROOT}/lib64 2>/dev/null || true")

    with open(f"{DB}/{pkg}/files", "w") as f:
        f.write("\n".join(files) + "\n")

    setuid = f"{pkg_dir}/setuid"
    if os.path.exists(setuid):
        with open(setuid) as f:
            for line in f.read().splitlines():
                line = line.strip()
                if line and os.path.isfile(line):
                    os.chmod(line, os.stat(line).st_mode | 0o4755)

    print(f"==> {pkg} installed")

def remove(pkg):
    if not installed(pkg):
        print(f"error: {pkg} is not installed")
        sys.exit(1)
    files_list = f"{DB}/{pkg}/files"
    if os.path.exists(files_list):
        with open(files_list) as f:
            for line in f.read().splitlines():
                line = line.strip()
                if line and os.path.isfile(line):
                    os.remove(line)
    shutil.rmtree(f"{DB}/{pkg}")
    print(f"==> {pkg} removed")

def clean(pkg=None):
    if pkg:
        path = f"{BUILD_DIR}/{pkg}"
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"==> cleaned {pkg}")
        else:
            print(f"==> nothing to clean for {pkg}")
    else:
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
            print(f"==> cleaned {BUILD_DIR}")
        else:
            print("==> nothing to clean")

def list_installed():
    if not os.path.exists(DB):
        print("no packages installed")
        return
    for pkg in sorted(os.listdir(DB)):
        print(pkg)

def sync():
    if os.path.exists(REPO):
        print("==> updating repo")
        run(f"git -C {REPO} pull")
    else:
        print("==> cloning repo")
        os.makedirs(os.path.dirname(REPO), exist_ok=True)
        run(f"git clone {REPO_URL} {REPO}")
    print("==> done")

def search(query):
    if not os.path.exists(REPO):
        print("error: repo not found")
        sys.exit(1)
    for pkg in sorted(os.listdir(REPO)):
        if query.lower() in pkg.lower():
            print(pkg)

def usage():
    print("usage: sxpkg <command> [package]")
    print("commands:")
    print("  sync           sync package repo")
    print("  install <pkg>  install a package")
    print("  remove <pkg>   remove a package")
    print("  list           list installed packages")
    print("  search <query> search packages in repo")
    print("  clean [pkg]    remove build cache")

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "sync":
        sync()
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("error: specify a package")
            sys.exit(1)
        if os.geteuid() != 0:
            print("error: run as root")
            sys.exit(1)
        for pkg in sys.argv[2:]:
            install(pkg)
    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("error: specify a package")
            sys.exit(1)
        if os.geteuid() != 0:
            print("error: run as root")
            sys.exit(1)
        remove(sys.argv[2])
    elif cmd == "list":
        list_installed()
    elif cmd == "clean":
        clean(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("error: specify a query")
            sys.exit(1)
        search(sys.argv[2])
    else:
        usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
