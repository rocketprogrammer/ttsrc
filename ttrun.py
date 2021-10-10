import sys
sys.path.append("./modules")

import os, marshal, imp
os.environ["PATH"] += ";./resources"

codes = {}
codes["otp"] = [1, None]
codes["toontown"] = [1, None]

def generate(path, module):
    print((path, module))

    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            generate(os.path.join(path, file), module + [file])

        elif file.endswith(".py"):
            if file == "__init__.py":
                codes[".".join(module)] = [1, os.path.join(path, file)]
            else:
                codes[".".join(module + [file[:-3]])] = [0, os.path.join(path, file)]


class Importer:
    @classmethod
    def find_module(cls, fullname, path=None):
        if fullname in codes:
            return cls


    @classmethod
    def load_module(cls, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        code = codes[fullname]
        module = imp.new_module(fullname)

        sys.modules[fullname] = module

        #module.__builtins__ = __builtins__
        module.__file__ = "<frozen>"
        module.__name__ = fullname
        module.__path__ = []
        module.__loader__ = cls

        if code[0] == 1:
            module.__package__ = fullname
        else:
            module.__package__ = ".".join(fullname.split(".")[:-1])

        if code[1]:
            with open(code[1], "r") as file:
                exec(compile(file.read() + "\n", codes[fullname][1], "exec"), module.__dict__)

        return module



if __name__ == "__main__":
    sys.meta_path.append(Importer)

    generate("direct/src", ["direct"])
    generate("toontown/src", ["toontown"])
    generate("otp/src", ["otp"])

    from pandac.PandaModules import VirtualFileSystem, Filename, loadPrcFileData
    vfs = VirtualFileSystem.getGlobalPtr()
    vfs.mount(Filename("resources"), '.', 0)
    for phase in [3,3.5,4,5,5.5,6,7,8,9,10,11,12,13]:
        vfs.mount(Filename("resources", "phase_" + str(phase) + ".mf"), '.', VirtualFileSystem.MFReadOnly)

    loadPrcFileData("", "dc-file resources/phase_3/etc/otp.dc")
    loadPrcFileData("", "dc-file resources/phase_3/etc/toon.dc")

    # we need some sql config
    loadPrcFileData("", "mysql-user root")
    loadPrcFileData("", "mysql-passwd root")
    loadPrcFileData("", "want-code-redemption-init-db 1")

    import traceback
    try:
        if "-ai" in sys.argv:
            from toontown.ai import AIStart

        elif "-ud" in sys.argv:
            from toontown.uberdog import Start

        else:
            from toontown.toonbase import ToontownStart

    except:
        traceback.print_exc()

    sys.exit()
