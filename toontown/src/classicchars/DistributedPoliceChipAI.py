from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.classicchars.DistributedChipAI import DistributedChipAI

class DistributedPoliceChipAI(DistributedChipAI):
    notify = directNotify.newCategory('DistributedPoliceChipAI')