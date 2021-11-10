import os

# out dirs
OUTDIR = "built-switch"

DIRECT = os.path.join(OUTDIR, "direct")
INCDIR = os.path.join(OUTDIR, "include")
LIBDIR = os.path.join(OUTDIR, "lib")
PANDAC = os.path.join(OUTDIR, "pandac")
PYTHON = os.path.join(OUTDIR, "python")
TMPDIR = os.path.join(OUTDIR, "tmp")

PYTHON_LIB = os.path.join(PYTHON, "Lib")
PANDAC_INPUT = os.path.join(PANDAC, "input")
INCDIR_OTP = os.path.join(INCDIR, "otp")
INCDIR_TOONTOWN = os.path.join(INCDIR, "toontown")

# devkit pro
DEVKITPRO = r"D:\devkitPro"

LIBNX_INCLUDE = os.path.join(DEVKITPRO, "libnx/include")
PORTLIBS_INCLUDE = os.path.join(DEVKITPRO, "portlibs/switch/include")

CC = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-gcc.exe")
CXX = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-g++.exe")
AR = os.path.join(DEVKITPRO, "devkitA64/bin/aarch64-none-elf-ar.exe")

# tools 
INTERROGATE = "built/bin/interrogate.exe"
INTERROGATE_MODULE = "built/bin/interrogate_module.exe"

FLEX = "thirdparty/win-util/flex.exe"
BISON = "thirdparty/win-util/bison.exe"
BISON_SIMPLE = "thirdparty/win-util/bison.simple"

COMPILE = "thirdparty/switch-python/compiler.exe"