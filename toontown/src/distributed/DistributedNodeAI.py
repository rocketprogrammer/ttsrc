from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import NodePath


class DistributedNodeAI(DistributedObjectAI, NodePath):
    def __init__(self, air, name=None):
        if name is None:
            name = self.__class__.__name__
        NodePath.__init__(self, name)
        DistributedObjectAI.__init__(self, air)
        self._zoneData = None

    @staticmethod
    def staticGetZoneChangeEvent(doId):
        return 'DOChangeZone-%s' % doId

    def setPosHpr(self, x, y, z, h, p, r):
        self.setPos(x, y, z)
        self.setHpr(h, p, r)

    def b_setPosHpr(self, x, y, z, h, p, r):
        self.setPosHpr(x, y, z, h, p, r)
        self.d_setPosHpr(x, y, z, h, p, r)

    def d_setPosHpr(self, x, y, z, h, p, r):
        self.sendUpdate('setPosHpr', [x, y, z, h, p, r])

    def d_setPos(self, x, y, z):
        self.sendUpdate('setPos', [x, y, z])

    def b_setParent(self, parentToken):
        self.setParent(parentToken)
        self.d_setParent(parentToken)

    def setParent(self, parentToken):
        self.do_setParent(parentToken)

    def d_setParent(self, parentToken):
        self.sendUpdate('setParent', [parentToken])

    def do_setParent(self, parentToken):
        self.getZoneData().getParentMgr().requestReparent(self, parentToken)

    def getZoneData(self):
        # Call this to get an AIZoneData object for the current zone.
        # This class will hold onto it as self._zoneData
        # setLocation destroys self._zoneData if we move away to
        # a different zone
        if self._zoneData is None:
            from toontown.ai.AIZoneData import AIZoneData
            self._zoneData = AIZoneData(self.air, self.parentId, self.zoneId)
        return self._zoneData

    def getCollTrav(self, *args, **kArgs):
        return self.getZoneData().getCollTrav(*args, **kArgs)
