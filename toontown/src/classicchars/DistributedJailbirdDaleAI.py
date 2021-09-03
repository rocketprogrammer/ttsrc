from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.classicchars.DistributedDaleAI import DistributedDaleAI

class DistributedJailbirdDaleAI(DistributedDaleAI):
    notify = directNotify.newCategory('DistributedJailbirdDaleAI')