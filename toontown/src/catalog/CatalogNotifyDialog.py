from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.gui.DirectGui import *
from pandac.PandaModules import *

class CatalogNotifyDialog:
    __module__ = __name__
    notify = DirectNotifyGlobal.directNotify.newCategory('CatalogNotifyDialog')

    def __init__(self, message):
        self.message = message
        self.messageIndex = 0
        self.frame = DirectFrame(relief=None, image=getDefaultDialogGeom(), image_color=ToontownGlobals.GlobalDialogColor, image_scale=(1.2, 1.0, 0.4), text=message[0], text_wordwrap=16, text_scale=0.06, text_pos=(-0.1, 0.1), pos=(0.4, 0, 0.78))
        buttons = loader.loadModelOnce('phase_3/models/gui/dialog_box_buttons_gui')
        cancelImageList = (
         buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
        okImageList = (
         buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
        self.nextButton = DirectButton(parent=self.frame, relief=None, image=okImageList, command=self.handleButton, pos=(0, 0, -0.14))
        self.doneButton = DirectButton(parent=self.frame, relief=None, image=cancelImageList, command=self.handleButton, pos=(0, 0, -0.14))
        if len(message) == 1:
            self.nextButton.hide()
        else:
            self.doneButton.hide()
        return

    def handleButton(self):
        self.messageIndex += 1
        if self.messageIndex >= len(self.message):
            self.cleanup()
            return
        self.frame['text'] = self.message[self.messageIndex]
        if self.messageIndex + 1 == len(self.message):
            self.nextButton.hide()
            self.doneButton.show()

    def cleanup(self):
        if self.frame:
            self.frame.destroy()
        self.frame = None
        self.nextButton = None
        self.doneButton = None
        return

    def __handleButton(self, value):
        self.cleanup()