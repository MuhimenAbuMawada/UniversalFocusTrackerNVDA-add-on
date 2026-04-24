# -*- coding: utf-8 -*-
# Universal Focus Tracker Add-on for NVDA
# Copyright (C) 2026 "Muhimen Nabeel", <07807761920nmn@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import wx
from gui import settingsDialogs 
import ui
import config
import eventHandler
from scriptHandler import script
import controlTypes
import winUser
import api
import tones
from . import settingsOptions
import addonHandler


addonHandler.initTranslation()


# A list for add-on settings in NVDA settings.
confSpec = {
    "enableTracking": "boolean(default=True)",
}

# initializing add-on.
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

# the default gestures dictionary.
    __gestures = {
        "kb:nvda+windows+t": "toggleTracking",
    }

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        config.conf.spec["mouseTracker"] = confSpec
        settingsDialogs.NVDASettingsDialog.categoryClasses.append(settingsOptions.SettingsDialog)
        self.navTimer = wx.Timer()
        self.navTimer.Bind(wx.EVT_TIMER, self.browserMode)
        self.timer = None
        self.lastPos = None

# A method to change the tracking status by a gesture.
    def script_toggleTracking(self, gesture):
        newState = not config.conf["mouseTracker"]["enableTracking"]
        config.conf["mouseTracker"]["enableTracking"] = newState
        config.conf.save()

        stateText = _("Enabled") if newState else _("Disabled")
        ui.message(_("Mouse tracking: ") + stateText)



    script_toggleTracking.category = _("Universal focus tracker")
    script_toggleTracking.__doc__ = _("Enable or disable mouse tracking")

# A function to support mouse movement in browsers because they need a little different method.
    def browserMode(self, event):
        if not config.conf["mouseTracker"]["enableTracking"]:
            return
        obj = api.getNavigatorObject()
        if not obj:
            return

        if obj.treeInterceptor and not obj.treeInterceptor.passThrough:
            self.moveMouseCursor(obj)


# This's the main function of this add-on, it moves the mouse cursor to NVDA object.
    def moveMouseCursor(self, obj = None):
        try:
            self.timer = None

            if obj is None:
                obj = api.getFocusObject()

            if not obj:
                return

# Adding an exception to avoid mouse movement in menus, because it causes problems.
            roles_to_ignore = (controlTypes.Role.POPUPMENU, controlTypes.Role.MENUBAR, controlTypes.Role.MENU, controlTypes.Role.MENUITEM)

            if obj.role in roles_to_ignore:
                return

            if obj.location:
                left, top, width, height = obj.location
                if width <= 0 or height <= 0:
                    return

# Fetching current focus measurements.
            x = left + (width // 2)
            y = top + (height // 2)
            if self.lastPos != (x, y):
                winUser.setCursorPos(x, y)
                # tones.beep(300, 50)
                self.lastPos = (x, y)

        except Exception as e:
            # print(f"Mouse Error: {e}")
            # tones.beep(2500, 200)
            # ui.message("Errror, couldn't move mouse cursor to NVDA cursor")
            pass


# A default function from NVDA which works with any focusing movement.
    def event_gainFocus(self, obj, nextHandler):
        if config.conf["mouseTracker"]["enableTracking"]:

# Checking if the focuse is in a browser or not and toggling the timer state accordingly.
            is_browser = obj.treeInterceptor and not obj.treeInterceptor.passThrough
            if is_browser:
                if not self.navTimer.IsRunning():
                    self.navTimer.Start(100)
                    # ui.message("Timer in browse mode Started")
            else:
                if self.navTimer.IsRunning():
                    self.navTimer.Stop()
                    # ui.message("Timer in browse mode Stopped")

            if self.timer:
                self.timer.Stop()
            self.timer = wx.CallLater(10, self.moveMouseCursor)
        nextHandler()

# It's also a default function which works when caret moves.
    def event_caret(self, obj, nextHandler):
        if config.conf["mouseTracker"]["enableTracking"]:
            if self.timer:
                self.timer.Stop()
            self.timer = wx.CallLater(10, self.moveMouseCursor)
        nextHandler()

# A function to terminate the add-on.
    def terminate(self):
        try:
            if self.navTimer:
                self.navTimer.Stop()
            settingsDialogs.NVDASettingsDialog.categoryClasses.remove(settingsOptions.SettingsDialog)
        except (ValueError, AttributeError):
            pass
        super(GlobalPlugin, self).terminate()