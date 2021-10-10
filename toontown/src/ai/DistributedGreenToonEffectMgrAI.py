from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.toonbase import ToontownGlobals

import time

class DistributedGreenToonEffectMgrAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedGreenToonEffectMgrAI')

    def addGreenToonEffect(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        if av.getCheesyEffect()[0] != ToontownGlobals.CEGreenToon:
            expireTime = int(time.time() / 60 + 0.5) + 3600
            av.b_setCheesyEffect(ToontownGlobals.CEGreenToon, 0, expireTime)

from .HolidayBaseAI import HolidayBaseAI

class GreenToonHolidayAI(HolidayBaseAI):

    def __init__(self, air, holidayId):
        HolidayBaseAI.__init__(self, air, holidayId)
        self.effectMgr = None

    def start(self):
        if not self.effectMgr:
            self.effectMgr = DistributedGreenToonEffectMgrAI(self.air)
            self.effectMgr.generateWithRequired(5819)

    def stop(self):
        if self.effectMgr:
            self.effectMgr.requestDelete()
            self.effectMgr = None