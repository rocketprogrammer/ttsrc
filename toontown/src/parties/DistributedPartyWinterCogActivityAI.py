from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.parties.DistributedPartyCogActivityAI import DistributedPartyCogActivityAI

class DistributedPartyWinterCogActivityAI(DistributedPartyCogActivityAI):
    notify = directNotify.newCategory('DistributedPartyWinterCogActivityAI')
