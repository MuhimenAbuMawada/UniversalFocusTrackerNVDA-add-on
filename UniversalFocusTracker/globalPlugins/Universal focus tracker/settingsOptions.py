# -*- coding: utf-8 -*-
# Universal Focus Tracker Add-on for NVDA
# Copyright (C) 2026 "Muhimen Nabeel", <07807761920nmn@gmail.com>
# This file is covered by the GNU General Public License.

import wx
from gui.settingsDialogs import SettingsPanel
import config


# Creating the catecory for add-on in NVDA settings.
class SettingsDialog(SettingsPanel):
	title = "Focus tracker"

# Creating widgets of add-on settings.
	def makeSettings(self, settingsSizer):
		self.enableTrackingCheckBox = wx.CheckBox(self, label="Enable tracking")
		state = config.conf["mouseTracker"]["enableTracking"]
		self.enableTrackingCheckBox.SetValue(state)
		settingsSizer.Add(self.enableTrackingCheckBox)

# This function is executed when pressing okay in add-on settings.
	def onSave(self):
		config.conf["mouseTracker"]["enableTracking"] = self.enableTrackingCheckBox.GetValue()