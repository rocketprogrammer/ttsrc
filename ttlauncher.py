from pandac.libpandaexpressModules import ExecutionEnvironment, ConfigPageManager

ExecutionEnvironment.setEnvironmentVariable("PRC_EXECUTABLE_ARGS", '-stdout')

cpMgr = ConfigPageManager.getGlobalPtr()
cpMgr.reloadImplicitPages()

from pandac.PandaModules import loadPrcFileData, VirtualFileSystem, Filename

loadPrcFileData("", "color-bits 8 8 8\nalpha-bits 8");
loadPrcFileData("", "default-server-constants 1\nfake-playtoken test\ngame-server 34.136.173.79\nverify-ssl 0\ntt-specific-login 1\nserver-version dev");
loadPrcFileData("", "want-magic-words 1")

vfs = VirtualFileSystem.getGlobalPtr()
for phase in [3,3.5,4,5,5.5,6,7,8,9,10,11,12,13]:
    vfs.mount(Filename("phase_" + str(phase) + ".mf"), '.', VirtualFileSystem.MFReadOnly)

from toontown.toonbase import ToontownStart