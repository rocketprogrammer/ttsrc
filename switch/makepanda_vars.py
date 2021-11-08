import os

OUTDIR = "built-switch"
INCDIR = os.path.join(OUTDIR, "include")
LIBDIR = os.path.join(OUTDIR, "lib")
TMPDIR = os.path.join(OUTDIR, "tmp")
PANDAC = os.path.join(OUTDIR, "pandac")
PINPUT = os.path.join(PANDAC, "input")

CC = r"D:\devkitPro\devkitA64\bin\aarch64-none-elf-gcc.exe"
CXX = r"D:\devkitPro\devkitA64\bin\aarch64-none-elf-g++.exe"
AR = r"D:\devkitPro\devkitA64\bin\aarch64-none-elf-ar.exe"

INTERROGATE = "built/bin/interrogate.exe"
INTERROGATE_MODULE = "built/bin/interrogate_module.exe"