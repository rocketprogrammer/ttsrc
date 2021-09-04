from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from .BattleBase import *

from direct.actor import Actor
from toontown.distributed import DelayDelete
from direct.directnotify import DirectNotifyGlobal
from . import DistributedBattleBase
from . import MovieUtil
from toontown.suit import Suit
from . import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from direct.fsm import State
import random

class DistributedBattleFinal(DistributedBattleBase.DistributedBattleBase):

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleFinal')

    def __init__(self, cr):
        """__init__(cr)
        """
        townBattle = cr.playGame.hood.loader.townBattle
        DistributedBattleBase.DistributedBattleBase.__init__(self, cr,
                                        townBattle)
        self.setupCollisions(self.uniqueBattleName('battle-collide'))

        self.bossCog = None
        self.bossCogRequest = None
        self.streetBattle = 0

        self.joiningSuitsName = self.uniqueBattleName('joiningSuits')

        # Add a new ReservesJoining state to the battle ClassicFSM
        self.fsm.addState(State.State('ReservesJoining',
                                      self.enterReservesJoining,
                                      self.exitReservesJoining,
                                      ['WaitForJoin']))
        offState = self.fsm.getStateNamed('Off')
        offState.addTransition('ReservesJoining')
        waitForJoinState = self.fsm.getStateNamed('WaitForJoin')
        waitForJoinState.addTransition('ReservesJoining')
        playMovieState = self.fsm.getStateNamed('PlayMovie')
        playMovieState.addTransition('ReservesJoining')

    def generate(self):
        """ generate()
        """
        DistributedBattleBase.DistributedBattleBase.generate(self)
        #dbgBattleMarkers = loader.loadModel("dbgBattleMarkers.egg")
        #dbgBattleMarkers.reparentTo(self)

    def disable(self):
        """ disable()
        """
        DistributedBattleBase.DistributedBattleBase.disable(self)
        base.cr.relatedObjectMgr.abortRequest(self.bossCogRequest)
        self.bossCogRequest = None
        self.bossCog = None

    def delete(self):
        """ delete()
        """
        DistributedBattleBase.DistributedBattleBase.delete(self)
        self.removeCollisionData()

    ##### Messages From The Server #####

    def setBossCogId(self, bossCogId):
        self.bossCogId = bossCogId

        if bossCogId in base.cr.doId2do:
            # This would be risky if we had toons entering the zone during
            # a battle--but since all the toons are always there from the
            # beginning, we can be confident that the BossCog has already
            # been generated by the time we receive the generate for its
            # associated battles.
            #RAU slightly modified so I can spy on the lawbot boss battle
            tempBossCog = base.cr.doId2do[bossCogId]
            self.__gotBossCog([tempBossCog])
        else:
            self.notify.debug('doing relatedObjectMgr.request for bossCog')
            self.bossCogRequest = base.cr.relatedObjectMgr.requestObjects(
                [bossCogId], allCallback = self.__gotBossCog)
            


    def __gotBossCog(self, bossCogList):
        self.bossCogRequest = None
        self.bossCog = bossCogList[0]

        # Now that we know the BossCog, we can check to see if we
        # should have enabled collisions when we went into the
        # NoLocalToon state.
        currStateName = self.localToonFsm.getCurrentState().getName()
        if currStateName == 'NoLocalToon' and self.bossCog.hasLocalToon():
            self.enableCollision()
        
    def setBattleNumber(self, battleNumber):
        self.battleNumber = battleNumber

    def setBattleSide(self, battleSide):
        self.battleSide = battleSide

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive,
                         suitsLured, suitTraps,
                         toons, toonsJoining, toonsPending, toonsActive,
                         toonsRunning, timestamp):
        if self.battleCleanedUp():
            return
        
        oldtoons = DistributedBattleBase.DistributedBattleBase.setMembers(self,
                suits, suitsJoining, suitsPending, suitsActive, suitsLured,
                suitTraps,
                toons, toonsJoining, toonsPending, toonsActive, toonsRunning,
                timestamp)

        # If the battle is full, we need to make the collision sphere
        # tangible so other toons can't walk through the battle
        if (len(self.toons) == 4 and len(oldtoons) < 4):
            self.notify.debug('setMembers() - battle is now full of toons')
            self.closeBattleCollision()
        elif (len(self.toons) < 4 and len(oldtoons) == 4):
            self.openBattleCollision()

    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    def makeSuitJoin(self, suit, ts):
        """ makeSuitJoin(suit, ts)
        """
        self.notify.debug('makeSuitJoin(%d)' % suit.doId)

        # We override this function from the base class to play no
        # interval.  Instead, we synchronize the animation of all of
        # the joining suits in the ReservesJoining state.
        
        self.joiningSuits.append(suit)
        if (self.hasLocalToon()):
            self.d_joinDone(base.localAvatar.doId, suit.doId)

    def showSuitsJoining(self, suits, ts, name, callback):
        assert(len(suits) > 0)

        if self.bossCog == None:
            # Hmm, no boss cog?  Maybe not generated yet.
            return

        if self.battleSide:
            openDoor = Func(self.bossCog.doorB.request, 'open')
            closeDoor = Func(self.bossCog.doorB.request, 'close')
        else:
            openDoor = Func(self.bossCog.doorA.request, 'open')
            closeDoor = Func(self.bossCog.doorA.request, 'close')

        suitTrack = Parallel()

        delay = 0
        for suit in suits:
            """
            This is done by the AI now.
            if self.battleNumber == 2:
                # Battle 2 features skelecogs only.
                suit.makeSkeleton()
                suit.corpMedallion.hide()
                suit.healthBar.show()
                """

            suit.setState('Battle')
            #RAU lawbot boss battle hack, 
            if suit.dna.dept == 'l':
                suit.reparentTo(self.bossCog)
                suit.setPos(0, 0, 0)
            
            suit.setPos(self.bossCog, 0, 0, 0)
            suit.headsUp(self)

            suit.setScale(3.8 / suit.height)

            # Move all suits into position
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)

            suitTrack.append(Track(
                (delay, self.createAdjustInterval(suit, destPos, destHpr)),
                (delay + 1.5, suit.scaleInterval(1.5, 1))
                ))
            delay += 1

        if (self.hasLocalToon()):
            # Parent the camera to the battle and position it to watch the
            # suits join.
            camera.reparentTo(self)

            # Choose either a left or a right view at random.
            if random.choice([0, 1]):
                camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                camera.setPosHpr(-20, -4, 7, -60, 0, 0)

        done = Func(callback)
        track = Sequence(openDoor, suitTrack, closeDoor, done,
                         name = name)
        track.start(ts)
        self.storeInterval(track, name)

    # Specific State functions

    ##### Off state #####

    ##### WaitForInput state #####

    ##### PlayMovie state #####

    ##### Reward state #####

    def __playReward(self, ts, callback):
        toonTracks = Parallel()
        for toon in self.toons:
            toonTracks.append(Sequence(Func(toon.loop, 'victory'),
                                       Wait(FLOOR_REWARD_TIMEOUT),
                                       Func(toon.loop, 'neutral')))
        name = self.uniqueName('floorReward')
        track = Sequence(toonTracks, name=name)

        if self.hasLocalToon():
            camera.setPos(0, 0, 1)
            camera.setHpr(180, 10, 0)

        track += [
            self.bossCog.makeEndOfBattleMovie(self.hasLocalToon()),
            Func(callback)]
        
        self.storeInterval(track, name)
        track.start(ts)

    def enterReward(self, ts):
        self.notify.debug('enterReward()')
        self.disableCollision()
        self.delayDeleteMembers()
        self.__playReward(ts, self.__handleFloorRewardDone)
        return None

    def __handleFloorRewardDone(self):
        return None

    def exitReward(self):
        self.notify.debug('exitReward()')
        # In case the server finished first
        self.clearInterval(self.uniqueName('floorReward'), finish = 1)
        self._removeMembersKeep()
        NametagGlobals.setMasterArrowsOn(1)
        for toon in self.toons:
            toon.startSmooth()
        return None

    ##### Resume state #####

    def enterResume(self, ts=0):
        assert(self.notify.debug('enterResume()'))
        if (self.hasLocalToon()):
            self.removeLocalToon()

        self.fsm.requestFinalState()

    def exitResume(self):
        return None

    ##### ReservesJoining state #####

    def enterReservesJoining(self, ts=0):
        assert(self.notify.debug('enterReservesJoining()'))

        # Show a movie with the cogs emerging from the BossCog's belly.
        self.delayDeleteMembers()
        self.showSuitsJoining(self.joiningSuits, ts, self.joiningSuitsName,
                                self.__reservesJoiningDone)

    def __reservesJoiningDone(self):
        self._removeMembersKeep()
        self.doneBarrier()

    def exitReservesJoining(self):
        self.clearInterval(self.joiningSuitsName)

    #########################
    ##### LocalToon ClassicFSM #####
    #########################

    ##### HasLocalToon state #####

    ##### NoLocalToon state #####

    def enterNoLocalToon(self):
        self.notify.debug('enterNoLocalToon()')

        # Enable battle collision sphere, but only if localToon is
        # known to the BossCog.
        if self.bossCog != None and \
           self.bossCog.hasLocalToon():
            self.enableCollision()
        else:
            self.disableCollision()

        return None

    def exitNoLocalToon(self):
        # Disable battle collision sphere
        self.disableCollision()
        return None

    ##### WaitForServer state #####

    def enterWaitForServer(self):
        self.notify.debug('enterWaitForServer()')
        return None

    def exitWaitForServer(self):
        return None
