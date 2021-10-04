from .DistributedNodeAI import DistributedNodeAI

from direct.showbase.PythonUtil import randFloat
from direct.distributed.ClockDelta import globalClockDelta


class BroadcastTypes:
    FULL = 0
    XYH = 1
    XY = 2


def onlyChanged(flags, compare):
    return (flags & compare) != 0 and (flags & ~compare) == 0


def isThresholdEqual(value1, value2, threshold):
    return -threshold < (value1 - value2) < threshold


SmoothNodeEpsilon = 0.01


FLAG_NEW_X = 1
FLAG_NEW_Y = 1 << 1
FLAG_NEW_Z = 1 << 2
FLAG_NEW_H = 1 << 3
FLAG_NEW_P = 1 << 4
FLAG_NEW_R = 1 << 5


class DistributedSmoothNodeAI(DistributedNodeAI):
    def __init__(self, air, name=None):
        DistributedNodeAI.__init__(self, air, name)
        self.broadcastTime = 0.2
        self.broadcastType = BroadcastTypes.FULL
        self.broadcastFunc = self.broadcastFull

        self.recentSentLocation = 0
        self.recentSetLocation = 0

        self._storedPosHpr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._storeStop = False
        self.__broadcastPeriod = None

    def getPosHprBroadcastTaskName(self):
        return self.uniqueName('sendPosHpr')

    def getPosHpr(self):
        return list(self.getPos()) + list(self.getHpr())

    def b_clearSmoothing(self):
        self.d_clearSmoothing()
        self.clearSmoothing()

    def d_clearSmoothing(self):
        self.sendUpdate('clearSmoothing', [0])

    def clearSmoothing(self, bogus = None):
        pass

    def startPosHprBroadcast(self, stagger=0):
        # Set stagger to non-zero to randomly delay the initial task execution
        # over 'period' seconds, to spread out task processing over time
        # when a large number of SmoothNodes are created simultaneously.
        taskName = self.getPosHprBroadcastTaskName()
        # Broadcast our initial position
        self.b_clearSmoothing()
        self.sendEverything()
        self.setPosHprBroadcastPeriod(self.broadcastTime)

        taskMgr.remove(taskName)

        if self.broadcastType == BroadcastTypes.FULL:
            self.broadcastFunc = self.broadcastFull
        elif self.broadcastType == BroadcastTypes.XYH:
            self.broadcastFunc = self.broadcastXYH
        else:
            self.broadcastFunc = self.broadcastXY

        delay = 0.0
        if stagger:
            delay = randFloat(self.broadcastTime)
        if self.wantSmoothPosBroadcastTask():
            taskMgr.doMethodLater(self.__broadcastPeriod + delay,
                                  self._posHprBroadcast, taskName)

    def setPosHprBroadcastPeriod(self, period):
        # call this at any time to change the delay between broadcasts
        self.__broadcastPeriod = period

    def getPosHprBroadcastPeriod(self):
        # query the current delay between broadcasts
        return self.__broadcastPeriod

    def wantSmoothPosBroadcastTask(self):
        return True

    def stopPosHprBroadcast(self):
        taskMgr.remove(self.getPosHprBroadcastTaskName())

    def _posHprBroadcast(self, task):
        self.broadcastFunc()
        task.setDelay(self.__broadcastPeriod)
        return task.again

    def delete(self):
        self.stopPosHprBroadcast()
        DistributedNodeAI.delete(self)

    def sendEverything(self):
        self.sendUpdate('setSmPosHpr', self._storedPosHpr + [globalClockDelta.getRealNetworkTime(bits=16)])

    def broadcastFull(self):
        posHpr = self.getPosHpr()

        flags = 0

        for i in range(6):
            if not isThresholdEqual(self._storedPosHpr[i], posHpr[i], SmoothNodeEpsilon):
                self._storedPosHpr[i] = posHpr[i]
                flags |= 1 << i

        ts = globalClockDelta.getRealNetworkTime(bits=16)

        # if self.recentSentLocation != self.recentSetLocation:
        #     # location (zoneId) has changed, send out all info copy over 'set'
        #     # location over to 'sent' location
        #     self.recentSentLocation = self.recentSetLocation
        #     self._storeStop = False
        #
        #     args = self._storedPosHpr + [self.recentSetLocation, ts]
        #     self.sendUpdate('setSmPosHprL', args)
        if flags == 0:
            # No change.  Send one and only one "stop" message.
            if not self._storeStop:
                self._storeStop = True
                self.sendUpdate('setSmStop', [ts])
        else:
            self._storeStop = False
            if onlyChanged(flags, FLAG_NEW_H):
                self.sendUpdate('setSmH', [self._storedPosHpr[3], ts])
            elif onlyChanged(flags, FLAG_NEW_Z):
                self.sendUpdate('setSmZ', [self._storedPosHpr[2], ts])
            elif onlyChanged(flags, FLAG_NEW_X | FLAG_NEW_Z):
                self.sendUpdate('setSmXZ', [self._storedPosHpr[0], self._storedPosHpr[2], ts])
            elif onlyChanged(flags, FLAG_NEW_X | FLAG_NEW_Y | FLAG_NEW_Z):
                self.sendUpdate('setSmPos', self._storedPosHpr[:3] + [ts])
            elif onlyChanged(flags, FLAG_NEW_H | FLAG_NEW_P | FLAG_NEW_R):
                self.sendUpdate('setSmHpr', self._storedPosHpr[3:] + [ts])
            elif onlyChanged(flags, FLAG_NEW_X | FLAG_NEW_Y | FLAG_NEW_H):
                self.sendUpdate('setSmXYH', [self._storedPosHpr[0], self._storedPosHpr[1], self._storedPosHpr[3], ts])
            elif onlyChanged(flags, FLAG_NEW_X | FLAG_NEW_Y | FLAG_NEW_Z | FLAG_NEW_H):
                self.sendUpdate('setSmXYZH', self._storedPosHpr[:4] + [ts])
            else:
                self.sendUpdate('setSmPosHpr', self._storedPosHpr + [ts])

    def broadcastXYH(self):
        posHpr = self.getPosHpr()
        flags = 0

        if not isThresholdEqual(self._storedPosHpr[0], posHpr[0], SmoothNodeEpsilon):
            self._storedPosHpr[0] = posHpr[0]
            flags |= FLAG_NEW_X

        if not isThresholdEqual(self._storedPosHpr[1], posHpr[1], SmoothNodeEpsilon):
            self._storedPosHpr[1] = posHpr[1]
            flags |= FLAG_NEW_Y

        if not isThresholdEqual(self._storedPosHpr[3], posHpr[3], SmoothNodeEpsilon):
            self._storedPosHpr[3] = posHpr[3]
            flags |= FLAG_NEW_H

        ts = globalClockDelta.getRealNetworkTime(bits=16)

        if flags == 0:
            # No change.  Send one and only one "stop" message.
            if not self._storeStop:
                self._storeStop = True
                self.sendUpdate('setSmStop', [ts])
        else:
            self._storeStop = False
            if onlyChanged(flags, FLAG_NEW_H):
                self.sendUpdate('setSmH', [self._storedPosHpr[3], ts])
            elif onlyChanged(flags, FLAG_NEW_X | FLAG_NEW_Y):
                self.sendUpdate('setSmXY', self._storedPosHpr[:2] + [ts])
            else:
                self.sendUpdate('setSmXYH', [self._storedPosHpr[0], self._storedPosHpr[1], self._storedPosHpr[3], ts])

    def broadcastXY(self):
        posHpr = self.getPosHpr()
        flags = 0

        if not isThresholdEqual(self._storedPosHpr[0], posHpr[0], SmoothNodeEpsilon):
            self._storedPosHpr[0] = posHpr[0]
            flags |= FLAG_NEW_X

        if not isThresholdEqual(self._storedPosHpr[1], posHpr[1], SmoothNodeEpsilon):
            self._storedPosHpr[1] = posHpr[1]
            flags |= FLAG_NEW_Y

        ts = globalClockDelta.getRealNetworkTime(bits=16)

        if flags == 0:
            # No change.  Send one and only one "stop" message.
            if not self._storeStop:
                self._storeStop = True
                self.sendUpdate('setSmStop', [ts])
        else:
            self._storeStop = False
            self.sendUpdate('setSmXY', self._storedPosHpr[:2] + [ts])

    def setSmStop(self, t=None):
        pass

    # These have their FFI functions exposed for efficiency
    def setSmH(self, h, t=None):
        self.setH(h)

    def setSmZ(self, z, t=None):
        self.setZ(z)

    def setSmXY(self, x, y, t=None):
        self.setX(x)
        self.setY(y)

    def setSmXZ(self, x, z, t=None):
        self.setX(x)
        self.setZ(z)

    def setSmPos(self, x, y, z, t=None):
        self.setPos(x, y, z)

    def setSmHpr(self, h, p, r, t=None):
        self.setHpr(h, p, r)

    def setSmXYH(self, x, y, h, t=None):
        self.setX(x)
        self.setY(y)
        self.setH(h)

    def setSmXYZH(self, x, y, z, h, t=None):
        self.setPos(x, y, z)
        self.setH(h)

    def setSmPosHpr(self, x, y, z, h, p, r, t=None):
        self.setPosHpr(x, y, z, h, p, r)

    # Do we use these on the AIx?
    def setComponentX(self, x):
        self.setX(x)

    def setComponentY(self, y):
        self.setY(y)

    def setComponentZ(self, z):
        self.setZ(z)

    def setComponentH(self, h):
        self.setH(h)

    def setComponentP(self, p):
        self.setP(p)

    def setComponentR(self, r):
        self.setR(r)

    def getComponentX(self):
        return self.getX()

    def getComponentY(self):
        return self.getY()

    def getComponentZ(self):
        return self.getZ()

    def getComponentH(self):
        return self.getH()

    def getComponentP(self):
        return self.getP()

    def getComponentR(self):
        return self.getR()
