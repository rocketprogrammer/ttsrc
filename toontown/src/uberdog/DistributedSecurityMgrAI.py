from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

class DistributedSecurityMgrAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory('DistributedSecurityMgrAI')

    def requestAccountId(self, todo0, todo1, todo2):
        pass

    def requestAccountIdResponse(self, todo0, todo1):
        pass