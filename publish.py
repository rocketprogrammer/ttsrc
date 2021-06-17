import os, shutil, sys
import struct, shutil

PANDA       = r"built"
PANDA_BIN   = os.path.join(PANDA, "bin")
PANDA_INC   = os.path.join(PANDA, "include")
PANDA_LIBS  = os.path.join(PANDA, "lib")
PANDA_ETC   = os.path.join(PANDA, "etc")
PYTHON      = os.path.join(PANDA, "python")
PYTHON_LIBS = os.path.join(PYTHON, "libs")
PYTHON_INC  = os.path.join(PYTHON, "include")
PYTHON_DLLS = os.path.join(PYTHON, "DLLs")

TTSRC       = r"builtTT"
TTSRC_TMP   = os.path.join(TTSRC, "tmp")
TTSRC_CLIENT = os.path.join(TTSRC, "client")

RESOURCES   = r"resources"
    
def add(path, name, targetName=None):
    if not targetName:
        targetName = name
        
    path = os.path.join(path, name)
    if os.path.isfile(path):
        if os.path.isfile(os.path.join(TTSRC_CLIENT, targetName)) and not targetName.endswith(".mf"):
            os.remove(os.path.join(TTSRC_CLIENT, targetName))
            
        if not os.path.isfile(os.path.join(TTSRC_CLIENT, targetName)):
            shutil.copyfile(path, os.path.join(TTSRC_CLIENT, targetName))
    else:
        if os.path.isdir(os.path.join(TTSRC_CLIENT, targetName)):
            shutil.rmtree(os.path.join(TTSRC_CLIENT, targetName))
        shutil.copytree(path, os.path.join(TTSRC_CLIENT, targetName))


def hide(data):
    last = 99
    res = bytearray()
    for char in data:
        res.append(char - last & 255)
        last = char

    return bytes(res)
    
if not os.path.isdir(TTSRC_TMP):
    os.mkdir(TTSRC_TMP)

if not os.path.isdir(TTSRC_CLIENT):
    os.mkdir(TTSRC_CLIENT)

for file in os.listdir(TTSRC_CLIENT):
    path = os.path.join(TTSRC_CLIENT, file)
    if os.path.isfile(path):
        if not file.endswith(".mf"):
            os.remove(path)
    else:
        shutil.rmtree(path)
        
# entrypoint
# for now, we don't want to build the entrypoint with the `build` command,
# so we're just gonna put its source 
with open("ttlauncher.py", "rb") as file:
    launcher = file.read()
    
# we hide it a bit and we mark the end
launcher = hide(launcher) + b"\0" 

# load modules 
with open(os.path.join(TTSRC_TMP, "ttmodules.h"), "w") as file:
    # we write in the launcher
    codeFormatted = '{ ' + ", ".join("0x" + (format(char, "x").rjust(2, "0")) for char in launcher) + ' }'
    file.write("static unsigned char ENTRYPOINT[] = " + codeFormatted + ";\n")
    file.write("static const unsigned int ENTRYPOINT_SIZE = " + str(len(launcher)-1) + ";\n\n")
    
    if "-embed" in sys.argv:
        with open(os.path.join(TTSRC, "Toontown.bin"), "rb") as file:
            data = file.read()
            
        modules = {}

        index = 0
        while index < len(data):
            modType, nameLen, codeLen = struct.unpack("<BHI", data[index:index+7])
            name = data[index+7:index+7+nameLen].decode("ascii")
            code = data[index+7+nameLen:index+7+nameLen+codeLen]
            modules[name] = (modType, code)
            
            index += 7+nameLen+codeLen
        
        file.write("#define FROZEN_ENABLED\n");
        file.write("struct FrozenModule {\n")
        file.write("    char* name;\n")
        file.write("    int type;\n")
        file.write("    unsigned int length;\n")
        file.write("    char* code;\n")
        file.write("};\n\n")
        
        for name, data in sorted(modules.items()):
            codeName = "code" + "".join(x[0].upper() + x[1:] for x in name.split("."))
            codeFormatted = '{ ' + ", ".join("0x" + (format(char, "x").rjust(2, "0")) for char in data[1]) + ' }'
            file.write("static const unsigned char " + codeName + "[] = " + codeFormatted + ";\n")
            
        file.write("static struct FrozenModule FROZEN_MODULES[] = {\n")
            
        for name, data in sorted(modules.items()):
            codeName = "code" + "".join(x[0].upper() + x[1:] for x in name.split("."))
            file.write("    { \"" + name + "\", " + str(data[0]) + ", " + str(len(data[1])) + ", (char*)" + str(codeName) + " },\n")
            
        file.write("};\n")
        
    else:
        file.write("#undef FROZEN_ENABLED")

# build client
if os.system("cl ttclient.cpp /EHsc /I" + str(TTSRC_TMP) + " /I" + str(PYTHON_INC) + " /Fo" + os.path.join(TTSRC_TMP, "ttclient.obj") + " /link /OUT:" + os.path.join(TTSRC_TMP, "Toontown.exe") + " /LIBPATH:" + str(PYTHON_LIBS) + (" /SUBSYSTEM:windows /ENTRY:mainCRTStartup" if "-gui" in sys.argv else "")):
    sys.exit()

if os.system("cl ttconfigrc.cpp /EHsc /DUSE_ENGLISH /I" + str(TTSRC_TMP) + " /I" + str(PYTHON_INC) + " /I" + str(PANDA_INC) + " /Fo" + os.path.join(TTSRC_TMP, "ttconfigrc.obj") + " /link /OUT:" + os.path.join(TTSRC_TMP, "Configrc.exe") + " /LIBPATH:" + str(PYTHON_LIBS) + " /LIBPATH:" + str(PANDA_LIBS) + " Gdi32.lib user32.lib advapi32.lib"):
    sys.exit()
    
if os.system(r'"thirdparty\win-util\upx" ' + os.path.join(TTSRC_TMP, "Configrc.exe")):
    sys.exit()
    
if "-embed" in sys.argv:
    if os.system(r'"thirdparty\win-util\upx" ' + os.path.join(TTSRC_TMP, "Toontown.exe")):
        sys.exit()

add(TTSRC_TMP, "Toontown.exe")

# add files
if not "-embed" in sys.argv:
    add(TTSRC, "Toontown.bin")
    
add(TTSRC_TMP, "Configrc.exe")

for file in os.listdir(RESOURCES):
    add(RESOURCES, file)
    
add(PYTHON, "python26.dll")
add(PYTHON_DLLS, "unicodedata.pyd")
add(PYTHON_DLLS, "_ssl.pyd")
add(PYTHON_DLLS, "_socket.pyd")
add(PYTHON_DLLS, "_bsddb.pyd")
add(PANDA_BIN, "libpanda.dll")
add(PANDA_BIN, "libpandaexpress.dll")
add(PANDA_BIN, "libpandaphysics.dll")
add(PANDA_BIN, "libp3direct.dll")
add(PANDA_BIN, "libp3dtool.dll")
add(PANDA_BIN, "libp3dtoolconfig.dll")
add(PANDA_BIN, "libp3windisplay.dll")
add(PANDA_BIN, "libpandagl.dll")
add(PANDA_BIN, "libpandaode.dll")
add(PANDA_BIN, "libpandafx.dll")
add(PANDA_BIN, "libp3vision.dll")
add(PANDA_BIN, "libpandaskel.dll")
add(PANDA_BIN, "libtinydisplay.dll")
add(PANDA_BIN, "libotp.dll")
add(PANDA_BIN, "libtoontown.dll")
add(PANDA_BIN, "libp3miles_audio.dll")
add(PANDA_BIN, "cg.dll")
add(PANDA_BIN, "cgGL.dll")

shutil.rmtree(TTSRC_TMP)