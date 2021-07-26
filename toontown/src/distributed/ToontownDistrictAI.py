from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task
from otp.distributed.OtpDoGlobals import *
from otp.distributed.DistributedDistrictAI import DistributedDistrictAI
from toontown.distributed import ToontownDistrictStatsAI

class ToontownDistrictAI(DistributedDistrictAI):
    """
    See Also: "toontown/src/distributed/DistributedDistrict.py"
    """
    notify = directNotify.newCategory("ToontownDistrictAI")

    def __init__(self, air, name="untitled"):
        DistributedDistrictAI.__init__(self, air, name)
        self.avatarCount = 0
        self.newAvatarCount = 0
        self.updateFreq = 5

    def generate(self):
        DistributedDistrictAI.generate(self)
        self.pushDistrictStats(firstTime = True)

    def delete(self):
        DistributedDistrictAI.delete(self)

    def setAvatarCount(self, avatarCount):
        self.avatarCount = avatarCount

    def d_setAvatarCount(self, avatarCount):
        self.sendUpdate('setAvatarCount', [avatarCount])

    def b_setAvatarCount(self, avatarCount):
        self.setAvatarCount(avatarCount)
        self.d_setAvatarCount(avatarCount)

    def getAvatarCount(self):
        return self.avatarCount

    def setNewAvatarCount(self, newAvatarCount):
        self.newAvatarCount = newAvatarCount

    def d_setNewAvatarCount(self, newAvatarCount):
        self.sendUpdate('setNewAvatarCount', [newAvatarCount])

    def b_setNewAvatarCount(self, newAvatarCount):
        self.setNewAvatarCount(newAvatarCount)
        self.d_setNewAvatarCount(newAvatarCount)

    def getNewAvatarCount(self):
        return self.newAvatarCount

    def setStats(self, avatarCount, newAvatarCount):
        self.setAvatarCount(avatarCount)
        self.setNewAvatarCount(newAvatarCount)

    def d_setStats(self, avatarCount, newAvatarCount):
        self.sendUpdate('setStats', [avatarCount, newAvatarCount])

    def b_setStats(self, avatarCount,  newAvatarCount):
        self.setStats(avatarCount,  newAvatarCount)
        self.d_setStats(avatarCount,  newAvatarCount)

    def pushDistrictStats(self, task = None, firstTime = False):
        if self.isDeleted():
            return

        # the first time we're called, the AIR doesn't have a welcomeValleyManager yet
        if firstTime:
            wvCount = 0
        else:
            wvCount = self.air.getWelcomeValleyCount()

        avatarCount = self.air.getPopulation()
        self.b_setStats(avatarCount, wvCount)
        taskMgr.doMethodLater(self.updateFreq, self.pushDistrictStats, 'DistributedDistrictUpdate')
        self.air.writeServerStatus('', avatarCount, len(self.air.doId2do))