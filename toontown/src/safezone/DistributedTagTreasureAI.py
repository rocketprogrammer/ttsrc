from toontown.safezone.DistributedTreasureAI import DistributedTreasureAI
from direct.directnotify import DirectNotifyGlobal

class DistributedTagTreasureAI(DistributedTreasureAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTagTreasureAI')

    def __init__(self, air, treasurePlanner, treasureType, x, y, z):
        DistributedTreasureAI.__init__(self, air, treasurePlanner, treasureType, x, y, z)
