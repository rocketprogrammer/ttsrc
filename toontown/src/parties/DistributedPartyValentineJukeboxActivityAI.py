from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.parties.DistributedPartyJukeboxActivityBaseAI import DistributedPartyJukeboxActivityBaseAI
from toontown.parties import PartyGlobals

class DistributedPartyValentineJukeboxActivityAI(DistributedPartyJukeboxActivityBaseAI):
    notify = directNotify.newCategory('DistributedPartyValentineJukeboxActivityAI')

    def __init__(self, air, partyDoId, x, y, h):
        DistributedPartyJukeboxActivityBaseAI.__init__(self,
                                            air,
                                            partyDoId,
                                            x, y, h,
                                            PartyGlobals.ActivityIds.PartyValentineJukebox,
                                            PartyGlobals.PhaseToMusicData
                                            )