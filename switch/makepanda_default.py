from makepanda_vars import *
import os
import subprocess
import shutil
import fnmatch
    
    
def ShouldUpdate(source, dest):
    if not os.path.exists(dest):
        return True
        
    if os.path.getmtime(source) > os.path.getmtime(dest):
        return True
        
    return False
    

def GetDefines(opts):
    res = [
        "__SWITCH__",
        "NOTIFY_DEBUG"
    ]
    
    if opts:
        if "gles" in opts:
            res.append("OPENGLES_1")
        if "gles2" in opts:
            res.append("OPENGLES_2")
            
    return res
    
        
def GetIncludes(opts):
    res = [
        "thirdparty/switch-python",
        "thirdparty/switch-python/Include",
        LIBNX_INCLUDE,
        PORTLIBS_INCLUDE
    ]
    if opts:
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
    
    return res
    
    
def MakeDirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    

def Compile(path, opts=None, building=None, output=None):
    if not output:
        output = os.path.join(TMPDIR, ".".join(path.split(".")[:-1]) + ".o")
        
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
    cmd += ["-I", INCDIR]
    for inc in GetIncludes(opts):
        cmd += ["-I", inc]
    
    # output
    cmd += ["-o", output]
    
    if subprocess.call(cmd):
        raise Exception("Non null result (building %r)" % path)
        
    return output


def Library(name, files):
    path = os.path.join(LIBDIR, name)
    cmd = [AR, "rcs", path] + files
    
    if subprocess.call(cmd):
        raise Exception("Non null result")
        
    return path
        
        
def CopyFile(path, target, name=None):
    if not os.path.isdir(target):
        raise Exception("target does not exist")
        
    targetpath = os.path.join(target, name or os.path.basename(path))
    
    if ShouldUpdate(path, targetpath):
        shutil.copyfile(path, targetpath)


def CopyHeaders(path):
    for file in os.listdir(path):
        if file.split(".")[-1] in ("h", "i", "I", "T"):
            CopyFile(os.path.join(path, file), INCDIR)


def CopyFiles(path):
    for file in os.listdir(path):
        CopyFile(os.path.join(path, file), INCDIR)
            
            
def Interrogate(name, srcdir, module, library, files, skip=None, opts=None, building=None):
    if not name.endswith(".in"):
        raise Exception("bad filename")
    
    # out igate.cxx
    path_cxx = os.path.join(TMPDIR, name[:-3] + "_igate.cxx")
    path_obj = os.path.join(TMPDIR, name[:-3] + "_igate.o")
    path_in = os.path.join(PINPUT, name)
    
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
            
        cmd += ["-S", INCDIR]
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
        
    return Compile(path_cxx, opts=opts, building=building, output=path_obj)
    
    
def Module(name, module, library, files, opts=None):
    if not name.endswith(".o"):
        raise Exception("bad file name")
        
    path_cxx = os.path.join(TMPDIR, name[:-2] + ".cxx")
    path_obj = os.path.join(TMPDIR, name)
    
    if not os.path.exists(path_cxx):
        print("Module %s" % name)
        
        cmd = [INTERROGATE_MODULE]
        cmd += ["-oc", path_cxx]
        cmd += ["-module", module]
        cmd += ["-library", library]
        cmd += ["-python-native"]
        
        for file in files:
            if not file.endswith(".in"):
                raise Exception("bad file")
                
            cmd.append(os.path.join(PINPUT, file))
            
        if subprocess.call(cmd):
            raise Exception("Interrogate_module failed")
            
            
    return Compile(path_cxx, opts=opts, output=path_obj)
    
    
    


for path in (OUTDIR, INCDIR, LIBDIR, TMPDIR, PANDAC, PINPUT):
    MakeDirs(path)
    