from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.estate.DistributedStatuaryAI import DistributedStatuaryAI

class DistributedAnimatedStatuaryAI(DistributedStatuaryAI):
    notify = directNotify.newCategory('DistributedAnimatedStatuaryAI')