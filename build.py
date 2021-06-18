import os, ast, imp, re, zlib, sys, marshal, struct

PANDA = r"built"

sys.path = [
    r'modules',
    os.path.join(PANDA, "python", "DLLs"),
    os.path.join(PANDA, "python", "lib"),
    os.path.join(PANDA, "python", "lib", "plat-win"),
    os.path.join(PANDA, "python", "lib", "lib-tk"),
    os.path.join(PANDA, "python"),
    PANDA,
    os.path.join(PANDA, "bin"),
    os.path.join(PANDA, "python", "site-packages"),
]

class ImportWalker: 
    # special modules
    modules = {
        "toontown": "toontown/src",
        "otp": "otp/src"
    }
    
    def __init__(self):
        self.ignore = set()
        self.ignoreFailed = set()
        self.results = []
        
    def load_imports(self, module, importedBy = None):
        if module in self.ignore:
            return
            
        self.ignore.add(module)
        
        # can we find the module?
        module = self.find_module(module)
        
        if not module:
            #print("not found", fullname)
            return
        
        moduleType, moduleName, modulePath = module
        # we need the parents 
        moduleNameSplit = moduleName.split(".")
        for n in range(1, len(moduleNameSplit)):
            self.load_imports(".".join(moduleNameSplit[:n]), moduleName + " (auto)")
            
        self.results.append((moduleType, moduleName, modulePath, importedBy))
        
        for imported in self.find_imports(moduleName, modulePath):
            # relative module name
            if moduleType == 0:
                importedName = ".".join(moduleName.split(".")[:-1] + [imported[1]])
            else:
                importedName = ".".join(moduleName.split(".") + [imported[1]])
                
            importedModule = self.find_module(importedName)
            
            if not importedModule:
                importedName = imported[1]
                importedModule = self.find_module(importedName)
            
            if importedModule:
                self.load_imports(importedName, moduleName)
                if imported[0] == 1:
                    if self.find_module(importedName + "." + imported[2]):
                        self.load_imports(importedName + "." + imported[2], moduleName)
                        
            else:
                if not imported[1] in self.ignoreFailed:
                    self.ignoreFailed.add(imported[1])
                    print("module not found: %s (imported by %s)" % (imported[1], moduleName))
                    
    def find_imports(self, module, file_path):
        # not cached
        results = []
        
        with open(file_path, "r") as file:
            data = file.read().rstrip() + "\n"
        
        for node in ast.walk(ast.parse(data, module)):
            if isinstance(node, ast.Import):
                for name in node.names:
                    results.append((0, name.name))
                    
            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    results.append((1, node.module, name.name))
                    
        return results
            
    def find_module(self, fullname):
        module = fullname.split(".")
        parent = None
        
        # first, we check if it's a special module
        for n in reversed(range(1, len(module))):
            potential = ".".join(module[:n])
            if potential in ImportWalker.modules:
                # it is!
                parent = ImportWalker.modules[potential]
                module = module[n:]
                break
            
        if parent:
            path = os.path.join(parent, *module[:-1] + [module[-1] + ".py"])
            if os.path.isfile(path):
                return (0, fullname, path)
            else:
                path = os.path.join(parent, *module + ["__init__.py"])
                if os.path.isfile(path):
                    return (1, fullname, path)
                    
        elif not "-y" in sys.argv:
            for parent in sys.path:
                path = os.path.join(parent, *module[:-1] + [module[-1] + ".py"])
                if os.path.isfile(path):
                    return (0, fullname, path)
                else:
                    path = os.path.join(parent, *module + ["__init__.py"])
                    if os.path.isfile(path):
                        return (1, fullname, path)
        
if not os.path.exists("builtTT"):
    os.mkdir("builtTT")
    
if not os.path.exists("builtTT/cache"):
    os.mkdir("builtTT/cache")
    
cache_imports_file = "builtTT/cache/" + (".importsAI.json" if "-ai" in sys.argv else ".importsUD.json" if "-ud" in sys.argv else ".imports.json")
if not os.path.exists(cache_imports_file) or "-x" in sys.argv:
    walker = ImportWalker()
    
    if "-ai" in sys.argv:
        walker.load_imports("toontown.ai.AIStart")
    elif "-ud" in sys.argv:
        walker.load_imports("toontown.uberdog.Start")
    else:
        walker.load_imports("toontown.toonbase.ToontownStart")
    
    # pls libotp and libtoontown
    #walker.load_imports("libotp")
    #walker.load_imports("libtoontown")
    
    # we need encodings
    for file in os.listdir(r"built\python\Lib\encodings"):
        if file.endswith(".py"):
            walker.load_imports("encodings." + file[:-3])
    
    # anydbm want this
    walker.load_imports("dbhash")
    
    # localizer isnt compiled auto
    walker.load_imports("toontown.toonbase.TTLocalizerEnglish")
    walker.load_imports("otp.otpbase.OTPLocalizerEnglish")
    
    # get import from dc
    importRegex = re.compile(r"^from ([A-Za-z0-9-_.]+)(\/AI|)(\/UD|)(\/OV|) import ([A-Za-z0-9-_*]+)(\/AI|)(\/UD|)(\/OV|)", re.MULTILINE)
    dcFiles = []
    
    # otp.dc file
    with open("resources/phase_3/etc/otp.dc", "r") as f:
        dcFiles += importRegex.findall(f.read())
        
    # toon.dc file
    with open("resources/phase_3/etc/toon.dc", "r") as f:
        dcFiles += importRegex.findall(f.read())
        
    for pkg, pkgAi, pkgUd, pkgOv, name, nameAi, nameUd, nameOv in dcFiles:
        pkgAi = pkgAi[1:]
        pkgUd = pkgUd[1:]
        pkgOv = pkgUd[1:]
        nameAi = nameAi[1:]
        nameUd = nameUd[1:]
        nameOv = nameOv[1:]
        
        walker.load_imports(pkg)
        if pkgAi and ("-ai" in sys.argv or "-ud" in sys.argv):
            walker.load_imports(pkg + pkgAi)
        if pkgUd and "-ud" in sys.argv:
            walker.load_imports(pkg + pkgUd)
        if pkgOv:
            walker.load_imports(pkg + pkgOv)
            
        walker.load_imports(pkg + "." + name)
        if nameAi and ("-ai" in sys.argv or "-ud" in sys.argv):
            walker.load_imports(pkg + "." + name + nameAi)
        if nameUd and "-ud" in sys.argv:
            walker.load_imports(pkg + "." + name + nameUd)
        if nameOv:
            walker.load_imports(pkg + "." + name + nameOv)
            
    
    # cashbot hq are not imported automatically
    walker.load_imports("toontown.coghq.CashbotMintEntrance_Action00")
    walker.load_imports("toontown.coghq.CashbotMintBoilerRoom_Action00")
    walker.load_imports("toontown.coghq.CashbotMintBoilerRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintDuctRoom_Action00")
    walker.load_imports("toontown.coghq.CashbotMintDuctRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintGearRoom_Action00")
    walker.load_imports("toontown.coghq.CashbotMintGearRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintLavaRoomFoyer_Action00")
    walker.load_imports("toontown.coghq.CashbotMintLavaRoomFoyer_Action01")
    walker.load_imports("toontown.coghq.CashbotMintLavaRoomFoyer_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintLavaRoom_Action00")
    walker.load_imports("toontown.coghq.CashbotMintLobby_Action00")
    walker.load_imports("toontown.coghq.CashbotMintLobby_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintPaintMixer_Action00")
    walker.load_imports("toontown.coghq.CashbotMintPipeRoom_Action00")
    walker.load_imports("toontown.coghq.CashbotMintPipeRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintStomperAlley_Action00")
    walker.load_imports("toontown.coghq.CashbotMintBoilerRoom_Battle01")
    walker.load_imports("toontown.coghq.CashbotMintControlRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintDuctRoom_Battle01")
    walker.load_imports("toontown.coghq.CashbotMintGearRoom_Battle01")
    walker.load_imports("toontown.coghq.CashbotMintLavaRoomFoyer_Battle01")
    walker.load_imports("toontown.coghq.CashbotMintOilRoom_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintLobby_Battle01")
    walker.load_imports("toontown.coghq.CashbotMintPaintMixerReward_Battle00")
    walker.load_imports("toontown.coghq.CashbotMintPipeRoom_Battle01")
    
    walker.load_imports("toontown.coghq.LawbotOfficeEntrance_Action00") # entrance
    walker.load_imports("toontown.coghq.LawbotOfficeOilRoom_Battle00") # oil room (final)
    walker.load_imports("toontown.coghq.LawbotOfficeOilRoom_Battle01") # oil room (final)
    walker.load_imports("toontown.coghq.LawbotOfficeBoilerRoom_Security00")
    walker.load_imports("toontown.coghq.LawbotOfficeBoilerRoom_Battle00")
    walker.load_imports("toontown.coghq.LawbotOfficeGearRoom_Action00")
    walker.load_imports("toontown.coghq.LawbotOfficeLobby_Action00")
    walker.load_imports("toontown.coghq.LawbotOfficeGearRoom_Security00") # plus-room library with lights
    walker.load_imports("toontown.coghq.LawbotOfficeLobby_Trap00") # two laser puzzles
    walker.load_imports("toontown.coghq.LawbotOfficeDiamondRoom_Security00")
    walker.load_imports("toontown.coghq.LawbotOfficeDiamondRoom_Trap00") # diamond with laser grids
    walker.load_imports("toontown.coghq.LawbotOfficeGearRoom_Platform00") # crate stack with lifter/stompers
    walker.load_imports("toontown.coghq.LawbotOfficeLobby_Lights00") # barrels surrounded by lights
    walker.load_imports("toontown.coghq.LawbotOfficeBoilerRoom_Action01") # large room with many big goons
    walker.load_imports("toontown.coghq.LawbotOfficeDiamondRoom_Action00") # stompers and lights
    walker.load_imports("toontown.coghq.LawbotOfficeDiamondRoom_Action01") # filing cabinet wall, big goons
    walker.load_imports("toontown.coghq.LawbotOfficeLobby_Action01") # lights around central pillar, library maze
    walker.load_imports("toontown.coghq.LawbotOfficeDiamondRoom_Battle00")
    walker.load_imports("toontown.coghq.LawbotOfficeGearRoom_Battle00")
    
    walker.load_imports("toontown.coghq.BossbotCountryClubEntrance_Action00")
    walker.load_imports("toontown.coghq.BossbotCountryClubTeeOffRoom_Action00")
    walker.load_imports("toontown.coghq.BossbotCountryClubFairwayRoom_Battle00")
    walker.load_imports("toontown.coghq.BossbotCountryClubMazeRoom_Battle00")
    walker.load_imports("toontown.coghq.BossbotCountryClubMazeRoom_Battle01")
    walker.load_imports("toontown.coghq.BossbotCountryClubMazeRoom_Battle02")
    #walker.load_imports("toontown.coghq.BossbotCountryClubMazeRoom_Battle03")
    walker.load_imports("toontown.coghq.BossbotCountryClubGreenRoom_Action00")
    walker.load_imports("toontown.coghq.BossbotCountryClubKartRoom_Battle00")
    walker.load_imports("toontown.coghq.BossbotCountryClubPresidentRoom_Battle00")
    walker.load_imports("toontown.coghq.BossbotCountryClubTeeOffRoom_Action01")
    walker.load_imports("toontown.coghq.BossbotCountryClubTeeOffRoom_Action02")
    walker.load_imports("toontown.coghq.BossbotCountryClubGreenRoom_Action01")
    walker.load_imports("toontown.coghq.BossbotCountryClubGreenRoom_Action02")
    
    walker.load_imports("toontown.coghq.LawOffice_Spec_Tier0_a")
    walker.load_imports("toontown.coghq.LawOffice_Spec_Tier0_b")
    
    # we using old pytz so we can do this
    walker.load_imports("pytz.zoneinfo.US.Pacific")
    
    # we need these for dna
    walker.load_imports("toontown.hood.HQPeriscopeAnimatedProp")
    walker.load_imports("toontown.hood.HQTelescopeAnimatedProp")
    walker.load_imports("toontown.hood.FishAnimatedProp")
    walker.load_imports("toontown.hood.PetShopFishAnimatedProp")
    walker.load_imports("toontown.hood.TrashcanZeroAnimatedProp")
    walker.load_imports("toontown.hood.TrashcanOneAnimatedProp")
    walker.load_imports("toontown.hood.TrashcanTwoAnimatedProp")
    walker.load_imports("toontown.hood.MailboxZeroAnimatedProp")
    walker.load_imports("toontown.hood.MailboxOneAnimatedProp")
    walker.load_imports("toontown.hood.MailboxTwoAnimatedProp")
    walker.load_imports("toontown.hood.HydrantZeroAnimatedProp")
    walker.load_imports("toontown.hood.HydrantOneAnimatedProp")
    walker.load_imports("toontown.hood.HydrantTwoAnimatedProp")
    
    # and those need these
    walker.load_imports("toontown.hood.GenericAnimatedProp")
    walker.load_imports("toontown.hood.GenericAnimatedBuilding")
    walker.load_imports("toontown.hood.InteractiveAnimatedProp")
    walker.load_imports("toontown.hood.HydrantInteractiveProp")
    walker.load_imports("toontown.hood.TrashcanInteractiveProp")
    walker.load_imports("toontown.hood.MailboxInteractiveProp")
    
    results = walker.results
    
    import json
    with open(cache_imports_file, "w") as file:
        file.write(json.dumps(results, indent=4))
        
else:
    import json
    with open(cache_imports_file, "r") as file:
        results = json.loads(file.read())
        
class Transformer(ast.NodeTransformer):
    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):                      
            pass_ = ast.Pass()
            pass_.lineno = node.lineno
            pass_.col_offset = node.col_offset
            return pass_
            
        return node

data = {}
for mtype, module, filename, imported_by in results:
    if isinstance(module, unicode):
        module = module.encode("ascii")
        
    cache_path = "./builtTT/cache/" + module + ".pyc"

    if os.path.exists(cache_path) and int(os.path.getmtime(cache_path)) == int(os.path.getmtime(filename)):
        #print("compiling module " + str(module) + " (cached)")
        with open(cache_path, "rb") as file:
            code = file.read()
        
    else:
        with open(filename, "r") as file:
            source = file.read().rstrip() + "\n"
            
        #print("visiting module", module)
        tree = ast.parse(source, module)
        Transformer().visit(tree)
        
        #print("compiling module " + str(module))
        try:
            code = compile(tree, module, "exec") # changed `tree` => `data`
        except SyntaxError as e:
            print("syntax error from %s: %s" % (module, e))
            
            code = compile(source, module, "exec")
            
        code = marshal.dumps(code)
        
        with open(cache_path, "wb") as file:
            file.write(code)
            
        os.utime(cache_path, (int(os.path.getmtime(filename)), int(os.path.getmtime(filename))))
        
    data[module] = (mtype, code)
    
    if (".ai" in module or "AI" in module or ".uberdog" in module or "UD" in module) and not ("-ai" in sys.argv or "-ud" in sys.argv):
        print("WARNING: " + str(module) + " (imported_by: " + str(imported_by) + ")")

if "-ai" in sys.argv:
    outfile = "ToontownAI.bin"
elif "-ud" in sys.argv:
    outfile = "ToontownUD.bin"
else:
    outfile = "Toontown.bin"
    
result = ""

for name, (mtype, code) in data.items():
    result += struct.pack("<BHI", mtype, len(name), len(code))
    result += name + code
    
#print("TODO", marshalled.keys())
with open("builtTT/" + outfile, "wb") as file:
    file.write(result)
    