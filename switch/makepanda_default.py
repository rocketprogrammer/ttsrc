from makepanda_vars import *
import os
import subprocess
import shutil
import fnmatch
import threading


_FsLock = threading.Lock()
_OptLevel = 0

def SetOptimisationLevel(level):
    global _OptLevel
    _OptLevel = level
    

def MakeDirs(path):
    with _FsLock:
        if not os.path.isdir(path):
            os.makedirs(path)
    
    
def CopyFile(path, target):
    MakeDirs(os.path.dirname(target))
    with _FsLock:
        if ShouldUpdate(path, target):
            shutil.copyfile(path, target)
    
    
def MoveFile(path, target):
    with _FsLock:
        if os.path.isfile(target):
            os.remove(target)
        os.rename(path, target)
    
    
def CopyFileTo(path, target, name=None):
    targetpath = os.path.join(target, name or os.path.basename(path))
    CopyFile(path, targetpath)


def CopyHeaders(path, target=INCDIR):
    for file in os.listdir(path):
        if os.path.splitext(file)[1] in (".h", ".i", ".I", ".T"):
            CopyFileTo(os.path.join(path, file), target)


def CopyIncludeFiles(path, target=INCDIR):
    for file in os.listdir(path):
        CopyFileTo(os.path.join(path, file), target)

    
def ShouldUpdate(source, dest):
    if not os.path.exists(dest):
        return True
        
    if os.path.getmtime(source) > os.path.getmtime(dest):
        return True
        
    return False
    

def GetDefines(opts):
    res = [
        "__SWITCH__",
        "LINK_ALL_STATIC",
        "WITHIN_PANDA",
        "WANT_NATIVE_NET"
    ]
    
    if _OptLevel <= 1:
        res.append("_DEBUG")
        
    elif _OptLevel >= 3:
        res.append("NDEBUG")
    
    if opts:
        if "gl" in opts:
            res.append("OPENGL")
        if "gles" in opts:
            res.append("OPENGLES_1")
        if "gles2" in opts:
            res.append("OPENGLES_2")
            
    return res
    
        
def GetIncludes(opts):
    res = [
        INCDIR
    ]
    
    if opts:
        if "otp" in opts:
            res.append(INCDIR_OTP)
        if "toontown" in opts:
            res.append(INCDIR_TOONTOWN)
        if "zlib" in opts:
            res.append("thirdparty/switch-libs/zlib/include")
        if "fftw" in opts:
            res.append("thirdparty/switch-libs/fftw/include")
        if "freetype" in opts:
            res.append("thirdparty/switch-libs/freetype/include")
        if "jpeg" in opts:
            res.append("thirdparty/switch-libs/jpeg/include")
        if "png" in opts:
            res.append("thirdparty/switch-libs/png/include")
        if "ode" in opts:
            res.append("thirdparty/switch-libs/ode/include")
        if "openssl" in opts:
            res.append("thirdparty/switch-libs/openssl/include")
        if "openal" in opts:
            res.append("thirdparty/switch-libs/openal/include")
        if "opus" in opts:
            res.append("thirdparty/switch-libs/opus/include")
        if "gl" in opts:
            res.append("thirdparty/switch-libs/glad/include")
        if "egl" in opts:
            res.append("thirdparty/switch-libs/egl/include")
            
            
    res += [
        "thirdparty/switch-python",
        "thirdparty/switch-python/Include",
        LIBNX_INCLUDE
    ]
    
    return res
    
    
def _CompileCxx(path, opts=None, building=None, output=None):
    if not output:
        output = os.path.join(TMPDIR, os.path.splitext(path)[0] + ".o")
        
    # if source file is older than dest, then we don't care
    if not ShouldUpdate(path, output):
        return output
        
    MakeDirs(os.path.dirname(output))
    print("Compiling %s" % path)
        
    if path.endswith(".c"):
        cmd = [CC, "-fPIC", "-pthread"]
    elif path.endswith(".cxx"):
        cmd = [CXX, "-fPIC", "-pthread", "-Wno-register", "-ftemplate-depth-30"]
    else:
        raise Exception("Invalid file %r" % path)
    
    # optimisations
    if _OptLevel >= 4:
        cmd += ["-Ofast"]
    else:
        cmd += ["-O" + str(_OptLevel)]
        
    # ARCH
    cmd += ["-march=armv8-a+crc+crypto", "-mtune=cortex-a57", "-mtp=soft"]
    cmd += ["-c", path]
    
    # defines
    for defi in GetDefines(opts):
        cmd += ["-D" + defi]
    
    # building
    if building:
        cmd.append("-DBUILDING_" + building)
    
    # includes
    for inc in GetIncludes(opts):
        cmd += ["-I", inc]
    
    # output
    cmd += ["-o", output]
    
    if subprocess.call(cmd):
        raise Exception("Non null result (building %r)" % path)
        
    return output
    
    
def _CompileFlex(path, prefix, dashi=False, building=None, opts=None):
    # To compile a flex (.lxx),
    # we first need to create a cxx (using the flex command),
    # then we compile it.
    
    # Expected final path
    path_out_cxx = os.path.join(TMPDIR, path + ".cxx")
    
    # Checking if an update is necssary
    if ShouldUpdate(path, path_out_cxx):
        # We create the outdir if it doesn't exist
        MakeDirs(os.path.dirname(path_out_cxx))
        
        cmd = [FLEX]
        if dashi:
            cmd.append("-i")
        
        cmd.append("-P" + prefix)
        cmd.append("-o" + path_out_cxx)
        cmd.append(path)
        
        # Calling flex
        print("Flex %s" % path)
        if subprocess.call(cmd):
            raise Exception("flex failed")
        
    # Path of output
    output = os.path.join(TMPDIR, path + ".o")
    return _CompileCxx(path_out_cxx, opts=opts, building=building, output=output)
    
    
def _CompileBison(path, prefix, building=None, opts=None, include=INCDIR):
    ifile = os.path.basename(path)
    
    # Expected final path
    path_h = os.path.join(include, ifile[:-4] + ".h")
    path_cxx = os.path.join(TMPDIR, path + ".cxx")
    
    if ShouldUpdate(path, path_h) or ShouldUpdate(path, path_cxx):
        # Paths of files generated by bison
        path_out_h = os.path.join(TMPDIR, path + ".h")
        path_out_c = os.path.join(TMPDIR, path + ".c")
        
        # We create the outdir if it doesn't exist
        MakeDirs(os.path.dirname(path_out_h))
        
        print("Bison %s" % path)
        if subprocess.call([BISON, "-y", "-d", "-o", path_out_c, "-p", prefix, path], env={"BISON_SIMPLE": BISON_SIMPLE}):
            raise Exception("bison failed")
        
        # We move the generated files
        # (they should be in the same directory as path_out_h and path_out_c,
        #  so we're not recreating the directories)
        MoveFile(path_out_h, path_h)
        MoveFile(path_out_c, path_cxx)
        
    
    output = os.path.join(TMPDIR, path + ".o")
    return _CompileCxx(path_cxx, opts=opts, building=building, output=output)
    
    
def _CompilePython(path, output):
    if ShouldUpdate(path, output):
        MakeDirs(os.path.dirname(output))
        if subprocess.call([COMPILE, path, output]):
            #raise Exception("compile failed")
            print("! compile failed for %r" % path)
            pass
            
    return output

    
def Compile(path, *args, **kwargs):
    if path.endswith(".c") or path.endswith(".cxx"):
        return _CompileCxx(path, *args, **kwargs)
        
    elif path.endswith(".yxx"):
        return _CompileBison(path, *args, **kwargs)
        
    elif path.endswith(".lxx"):
        return _CompileFlex(path, *args, **kwargs)
        
    elif path.endswith(".py"):
        return _CompilePython(path, *args, **kwargs)
        
    else:
        raise Exception("Tried to compile %r" % path)


def Library(name, files):
    path = os.path.join(LIBDIR, name)
    cmd = [AR, "rcs", path] + files
    
    if subprocess.call(cmd):
        raise Exception("Non null result")
        
    return path
        
        
def Interrogate(name, srcdir, module, library, files, skip=None, opts=None, building=None):
    if not name.endswith(".in"):
        raise Exception("bad filename")
    
    # out igate.cxx
    path_cxx = os.path.join(TMPDIR, name[:-3] + "_igate.cxx")
    path_obj = os.path.join(TMPDIR, name[:-3] + "_igate.o")
    path_in = os.path.join(PANDAC_INPUT, name)
    
    if not os.path.exists(path_in) or not os.path.exists(path_cxx):
        print("Interrogate %s" % name)
        
        # most of this is from makepanda.py,
        # so idk anything about this
        cmd = [INTERROGATE]
        cmd += ["-srcdir", srcdir]
        cmd += ["-I", srcdir]
        cmd += ["-Dvolatile", "-Dmutable"]
        
        cmd += ["-DCPPPARSER", "-D__STDC__=1", "-D__cplusplus", "-D__inline", "-D__const=const",  "-D_LP64"]
        
        cmd += ["-oc", path_cxx, "-od", path_in]
        cmd += ["-fnames", "-string", "-refcount", "-assert", "-python-native"]
        
        cmd += ["-S", os.path.join(INCDIR, "parser-inc")]
        
        for inc in GetIncludes(opts):
            if "devkitPro" in inc:
                continue
                
            cmd += ["-S", inc]
            
        for defi in GetDefines(opts):
            cmd += ["-D" + defi]
            
        if building:
            cmd += ["-DBUILDING_" + building]
            
        cmd += ["-module", module]
        cmd += ["-library", library]
        
        for filename in os.listdir(srcdir):
            for pattern in (skip or ()):
                if fnmatch.fnmatch(filename, pattern):
                    break
                    
            else:
                # no break: no "skip" pattern
                for pattern in files:
                    if fnmatch.fnmatch(filename, pattern):
                        cmd.append(filename)
                        break
                    
        if subprocess.call(cmd):
            raise Exception("Interrogate failed")
        
    return _CompileCxx(path_cxx, opts=opts, building=building, output=path_obj)
    
    
def Module(name, module, library, files, opts=None):
    if not name.endswith(".o"):
        raise Exception("bad file name")
        
    path_cxx = os.path.join(TMPDIR, name[:-2] + ".cxx")
    path_obj = os.path.join(TMPDIR, name)
    
    for file in files:
        if ShouldUpdate(os.path.join(PANDAC_INPUT, file), path_cxx):
            break
    else:
        # no files should be updated
        return path_obj
    
    print("Module %s" % name)
    
    cmd = [INTERROGATE_MODULE]
    cmd += ["-oc", path_cxx]
    cmd += ["-module", module]
    cmd += ["-library", library]
    cmd += ["-python-native"]
    
    for file in files:
        if not file.endswith(".in"):
            raise Exception("bad file")
            
        cmd.append(os.path.join(PANDAC_INPUT, file))
        
    if subprocess.call(cmd):
        raise Exception("Interrogate_module failed")
            
            
    return _CompileCxx(path_cxx, opts=opts, output=path_obj)
    
    
    


for path in (OUTDIR, 
             DIRECT, INCDIR, LIBDIR, PANDAC, PYTHON, TMPDIR,
             PYTHON_LIB, PANDAC_INPUT, INCDIR_OTP, INCDIR_TOONTOWN):
    MakeDirs(path)
    