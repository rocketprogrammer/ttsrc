import os

OUTDIR = "built-switch"
INCDIR = os.path.join(OUTDIR, "include")
LIBDIR = os.path.join(OUTDIR, "lib")
TMPDIR = os.path.join(OUTDIR, "tmp")
PANDAC = os.path.join(OUTDIR, "pandac")
PINPUT = os.path.join(PANDAC, "input")

DEVKITPRO = r"D:\devkitPro"

LIBNX_INCLUDE = os.path.join(DEVKITPRO, "libnx/include")
PORTLIBS_INCLUDE = os.path.join(DEVKITPRO, "portlibs/switch/include")

CC = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-gcc.exe")
CXX = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-g++.exe")
AR = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-ar.exe")

INTERROGATE = "built/bin/interrogate.exe"
INTERROGATE_MODULE = "built/bin/interrogate_module.exe"