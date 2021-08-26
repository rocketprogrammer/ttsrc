from direct.gui.DirectGui import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import ToontownGlobals
from direct.showbase import DirectObject
from . import CatalogItem
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from direct.showbase import PythonUtil

class MailboxScreen(DirectObject.DirectObject):
    __module__ = __name__
    notify = directNotify.newCategory('MailboxScreen')

    def __init__(self, mailbox, avatar, doneEvent=None):
        self.mailbox = mailbox
        self.avatar = avatar
        self.items = self.avatar.mailboxContents
        self.doneEvent = doneEvent
        self.itemIndex = 0
        self.itemPanel = None
        self.ival = None
        self.itemText = None
        self.acceptingIndex = None
        self.numAtticAccepted = 0
        self.acceptErrorDialog = None
        self.load()
        self.hide()
        return

    def show(self):
        self.frame.show()
        self.__showCurrentItem()

    def hide(self):
        self.frame.hide()

    def load(self):
        model = loader.loadModel('phase_5.5/models/gui/package_delivery_panel')
        background = model.find('**/bg')
        itemBoard = model.find('**/item_board')
        self.frame = DirectFrame(scale=1.1, relief=FLAT, frameSize=(-0.5, 0.5, -0.45, -0.05), frameColor=(0.737, 0.573, 0.345, 1.0))
        self.background = DirectFrame(self.frame, image=background, image_scale=0.05, relief=None, pos=(0, 1, 0))
        self.itemBoard = DirectFrame(parent=self.frame, image=itemBoard, image_scale=0.05, image_color=(0.922, 0.922, 0.753, 1), relief=None, pos=(0, 1, 0))
        self.itemCountLabel = DirectLabel(parent=self.frame, relief=None, text=self.__getNumberOfItemsText(), text_wordwrap=16, pos=(0.0, 0.0, 0.7), scale=0.09)
        exitUp = model.find('**/bu_return_rollover')
        exitDown = model.find('**/bu_return_rollover')
        exitRollover = model.find('**/bu_return_rollover')
        exitUp.setP(-90)
        exitDown.setP(-90)
        exitRollover.setP(-90)
        self.exitButton = DirectButton(parent=self.frame, relief=None, image=(exitUp, exitDown, exitRollover, exitUp), pos=(-0.01, 1.0, -0.36), scale=0.048, text=('', TTLocalizer.MailboxExitButton, TTLocalizer.MailboxExitButton, ''), text_scale=1.0, text_pos=(0, -0.08), textMayChange=0, command=self.__handleExit)
        self.gettingText = DirectLabel(parent=self.frame, relief=None, text='', text_wordwrap=10, pos=(0.0, 0.0, 0.32), scale=0.09)
        self.gettingText.hide()
        self.itemText = DirectLabel(parent=self.frame, relief=None, text='', text_wordwrap=16, pos=(0.0, 0.0, -0.025), scale=0.09)
        self.itemText.hide()
        acceptUp = model.find('**/bu_check_up')
        acceptDown = model.find('**/bu_check_down')
        acceptRollover = model.find('**/bu_check_rollover')
        acceptUp.setP(-90)
        acceptDown.setP(-90)
        acceptRollover.setP(-90)
        self.acceptButton = DirectButton(parent=self.frame, relief=None, image=(acceptUp, acceptDown, acceptRollover, acceptUp), image3_color=(0.8, 0.8, 0.8, 0.6), pos=(-0.01, 1.0, -0.16), scale=0.048, text=('', TTLocalizer.MailboxAcceptButton, TTLocalizer.MailboxAcceptButton, ''), text_scale=1.0, text_pos=(0, -0.09), textMayChange=0, command=self.__handleAccept, state=DISABLED)
        nextUp = model.find('**/bu_next_up')
        nextUp.setP(-90)
        nextDown = model.find('**/bu_next_down')
        nextDown.setP(-90)
        nextRollover = model.find('**/bu_next_rollover')
        nextRollover.setP(-90)
        self.nextButton = DirectButton(parent=self.frame, relief=None, image=(nextUp, nextDown, nextRollover, nextUp), image3_color=(0.8, 0.8, 0.8, 0.6), pos=(0.31, 1.0, -0.26), scale=0.05, text=('', TTLocalizer.MailboxItemNext, TTLocalizer.MailboxItemNext, ''), text_scale=1, text_pos=(-0.2, 0.3), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), textMayChange=0, command=self.__nextItem, state=DISABLED)
        prevUp = model.find('**/bu_previous_up')
        prevUp.setP(-90)
        prevDown = model.find('**/bu_previous_down')
        prevDown.setP(-90)
        prevRollover = model.find('**/bu_previous_rollover')
        prevRollover.setP(-90)
        self.prevButton = DirectButton(parent=self.frame, relief=None, image=(prevUp, prevDown, prevRollover, prevUp), pos=(-0.35, 1, -0.26), scale=0.05, image3_color=(0.8, 0.8, 0.8, 0.6), text=('', TTLocalizer.MailboxItemPrev, TTLocalizer.MailboxItemPrev, ''), text_scale=1, text_pos=(0, 0.3), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), textMayChange=0, command=self.__prevItem, state=DISABLED)
        return

    def unload(self):
        self.__clearCurrentItem()
        self.frame.destroy()
        del self.frame
        del self.mailbox
        if self.acceptErrorDialog:
            self.acceptErrorDialog.cleanup()
            self.acceptErrorDialog = None
        for item in self.items:
            item.acceptItemCleanup()

        self.ignoreAll()
        return

    def __handleExit(self):
        if self.numAtticAccepted == 0:
            self.__acceptExit()
        elif self.numAtticAccepted == 1:
            self.acceptErrorDialog = TTDialog.TTDialog(style=TTDialog.Acknowledge, text=TTLocalizer.CatalogAcceptInAttic, text_wordwrap=15, command=self.__acceptExit)
            self.acceptErrorDialog.show()
        else:
            self.acceptErrorDialog = TTDialog.TTDialog(style=TTDialog.Acknowledge, text=TTLocalizer.CatalogAcceptInAtticP, text_wordwrap=15, command=self.__acceptExit)
            self.acceptErrorDialog.show()

    def __acceptExit(self, buttonValue=None):
        self.hide()
        self.unload()
        messenger.send(self.doneEvent)

    def __handleAccept(self):
        if self.acceptingIndex != None:
            return
        self.acceptingIndex = self.itemIndex
        self.acceptButton['state'] = DISABLED
        self.__showCurrentItem()
        item = self.items[self.itemIndex]
        item.acceptItem(self.mailbox, self.acceptingIndex, self.__acceptItemCallback)
        return

    def __acceptItemCallback(self, retcode, item, index):
        if not hasattr(self, 'frame'):
            return
        if self.acceptingIndex != index:
            self.notify.warning('Got unexpected callback for index %s, expected %s.' % index)
            return
        self.acceptingIndex = None
        if retcode < 0:
            self.notify.info('Could not take item %s: retcode %s' % (item, retcode))
            self.acceptErrorDialog = TTDialog.TTDialog(style=TTDialog.CancelOnly, text=item.getAcceptItemErrorText(retcode), text_wordwrap=15, command=self.__acceptError)
            self.acceptErrorDialog.show()
        elif item.storedInAttic():
            self.numAtticAccepted += 1
            self.__acceptOk(index)
        else:
            callback = PythonUtil.Functor(self.__acceptOk, index)
            self.acceptErrorDialog = TTDialog.TTDialog(style=TTDialog.Acknowledge, text=item.getAcceptItemErrorText(retcode), text_wordwrap=15, command=callback)
            self.acceptErrorDialog.show()
        return

    def __acceptError(self, buttonValue=None):
        self.acceptErrorDialog.cleanup()
        self.acceptErrorDialog = None
        self.__showCurrentItem()
        return

    def __acceptOk(self, index, buttonValue=None):
        if self.acceptErrorDialog:
            self.acceptErrorDialog.cleanup()
            self.acceptErrorDialog = None
        self.items = self.avatar.mailboxContents
        if self.itemIndex > index or self.itemIndex >= len(self.items):
            self.itemIndex -= 1
        if len(self.items) == 0:
            self.__handleExit()
            return
        self.itemCountLabel['text'] = (
         self.__getNumberOfItemsText(),)
        self.__showCurrentItem()
        return

    def __getNumberOfItemsText(self):
        if len(self.items) == 1:
            return TTLocalizer.MailboxOneItem
        else:
            return TTLocalizer.MailboxNumberOfItems % len(self.items)

    def __clearCurrentItem(self):
        if self.itemPanel:
            self.itemPanel.destroy()
            self.itemPanel = None
        if self.ival:
            self.ival.finish()
            self.ival = None
        self.gettingText.hide()
        self.itemText.hide()
        self.acceptButton['state'] = DISABLED
        return

    def __showCurrentItem(self):
        self.__clearCurrentItem()
        item = self.items[self.itemIndex]
        if self.itemIndex == self.acceptingIndex:
            self.gettingText['text'] = TTLocalizer.MailboxGettingItem % item.getName()
            self.gettingText.show()
            return
        self.itemText['text'] = item.getName()
        self.itemText.show()
        (self.itemPanel, self.ival) = item.getPicture(base.localAvatar)
        if self.itemPanel:
            self.itemPanel.reparentTo(self.itemBoard, -1)
            self.itemPanel.setPos(0, 0, 0.35)
            self.itemPanel.setScale(0.25)
            self.itemText.setPos(0.0, 0.0, -0.025)
        else:
            self.itemText.setPos(0, 0, 0.3)
        if self.ival:
            self.ival.loop()
        if self.acceptingIndex == None:
            self.acceptButton['state'] = NORMAL
        if self.itemIndex > 0:
            self.prevButton['state'] = NORMAL
        else:
            self.prevButton['state'] = DISABLED
        if self.itemIndex + 1 < len(self.items):
            self.nextButton['state'] = NORMAL
        else:
            self.nextButton['state'] = DISABLED
        return

    def __nextItem(self):
        if self.itemIndex + 1 < len(self.items):
            self.itemIndex += 1
            self.__showCurrentItem()

    def __prevItem(self):
        if self.itemIndex > 0:
            self.itemIndex -= 1
            self.__showCurrentItem()