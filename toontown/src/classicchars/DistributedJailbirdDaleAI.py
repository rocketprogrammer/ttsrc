"""DistributedJailbirdDaleAI module: contains the DistributedJailbirdDaleAI class"""

from otp.ai.AIBaseGlobal import *
from toontown.classicchars import DistributedDaleAI
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.task import Task
import random
from toontown.toonbase import ToontownGlobals
from . import DistributedCCharBaseAI
from . import CharStateDatasAI
from toontown.toonbase import TTLocalizer

class DistributedJailbirdDaleAI(DistributedDaleAI.DistributedDaleAI):

    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedJailbirdDaleAI")

    def __init__(self, air):
        DistributedCCharBaseAI.DistributedCCharBaseAI.__init__(self, air, TTLocalizer.JailbirdDale)
        self.fsm = ClassicFSM.ClassicFSM('DistributedJailbirdDaleAI',
                           [State.State('Off',
                                        self.enterOff,
                                        self.exitOff,
                                        ['Lonely', 'TransitionToCostume', 'Walk']),
                            State.State('Lonely',
                                        self.enterLonely,
                                        self.exitLonely,
                                        ['Chatty', 'Walk', 'TransitionToCostume']),
                            State.State('Chatty',
                                        self.enterChatty,
                                        self.exitChatty,
                                        ['Lonely', 'Walk', 'TransitionToCostume']),
                            State.State('Walk',
                                        self.enterWalk,
                                        self.exitWalk,
                                        ['Lonely', 'Chatty', 'TransitionToCostume']),
                            State.State('TransitionToCostume',
                                            self.enterTransitionToCostume,
                                            self.exitTransitionToCostume,
                                            ['Off']),
                            ],
                           # Initial State
                           'Off',
                           # Final State
                           'Off',
                           )

        self.fsm.enterInitialState()
        
    def walkSpeed(self):
        return ToontownGlobals.DaleSpeed