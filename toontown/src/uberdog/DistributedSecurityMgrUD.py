from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class DistributedSecurityMgrUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('DistributedSecurityMgrUD')

    def requestAccountId(self, todo0, todo1, todo2):
        pass

    def requestAccountIdResponse(self, todo0, todo1):
        pass