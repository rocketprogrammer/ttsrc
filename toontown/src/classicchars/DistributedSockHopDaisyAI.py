from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.classicchars.DistributedDaisyAI import DistributedDaisyAI

class DistributedSockHopDaisyAI(DistributedDaisyAI):
    notify = directNotify.newCategory('DistributedSockHopDaisyAI')