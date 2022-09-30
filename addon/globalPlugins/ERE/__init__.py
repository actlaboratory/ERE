# coding: UTF-8

from __future__ import unicode_literals
import addonHandler
import gui
import globalPluginHandler
import globalVars
import threading
import time
import wx
import speech
import speechDictHandler
from copy import deepcopy
from logHandler import log
from .constants import *
from . import updater
from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter

try:
	import addonHandler
	addonHandler.initTranslation()
except:
	_ = lambda x : x


confspec = {
	"checkForUpdatesOnStartup": "boolean(default=True)",
	"enable": "boolean(default=True)",
}
config.conf.spec["ERE_global"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("English Reading Enhancer")

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		if self.getUpdateCheckSetting() is True:
			self.autoUpdateChecker = updater.AutoUpdateChecker()
			self.autoUpdateChecker.autoUpdateCheck()
		self._setupMenu()
		if self.getStateSetting():
			self._setup()
		t = threading.Thread(target=self._checkAutoLanguageSwitchingState, daemon=True)
		t.start()

	def _checkAutoLanguageSwitchingState(self):
		if self.getStateSetting() and config.conf["speech"]["autoLanguageSwitching"]:
			gui.messageBox(_("Automatic Language switching is enabled. English Reading Enhancer may not work correctly. To use this add-on, we recommend to disable this functionality."), _("Warning"))

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		try:
			gui.mainFrame.sysTrayIcon.menu.Remove(self.rootMenuItem)
		except BaseException:
			pass

	def _setup(self):
		if hasattr(speech, "speech"):
			self.processText_original = speech.speech.processText
		else:
			self.processText_original = speech.processText
		c = EnglishToKanaConverter()

		def processText(locale, text, symbolLevel):
			text = self.processText_original(locale, text, symbolLevel)
			if locale.startswith("ja") and self.getStateSetting():
				text = c.process(text)
			return text
		if hasattr(speech, "speech"):
			speech.speech.processText = processText
		else:
			speech.processText = processText
		# modify builtin speech dicts
		unusedEntries = []
		unusedPatterns = (
			"([a-z])([A-Z])",
			"([A-Z])([A-Z][a-z])",
		)
		for entry in speechDictHandler.dictionaries["builtin"]:
			if entry.pattern in unusedPatterns:
				unusedEntries.append(entry)
		self.builtinDict_original = deepcopy(speechDictHandler.dictionaries["builtin"])
		for entry in unusedEntries:
			index = speechDictHandler.dictionaries["builtin"].index(entry)
			del speechDictHandler.dictionaries["builtin"][index]

	def _unsetup(self):
		if hasattr(speech, "speech"):
			speech.speech.processText = self.processText_original
		else:
			speech.processText = self.processText_original
		speechDictHandler.dictionaries["builtin"] = self.builtinDict_original

	def _setupMenu(self):
		self.rootMenu = wx.Menu()
		self.stateToggleItem = self.rootMenu.Append(wx.ID_ANY, self.stateToggleString(), _("Toggles use of English Reading Enhancer."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.toggleState, self.stateToggleItem)
		self.updateCheckToggleItem = self.rootMenu.Append(wx.ID_ANY, self.updateCheckToggleString(), _("Toggles update checking on startup."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.toggleUpdateCheck, self.updateCheckToggleItem)
		self.updateCheckPerformItem = self.rootMenu.Append(wx.ID_ANY, _("Check for updates"), _("Checks for new updates manually."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.performUpdateCheck, self.updateCheckPerformItem)
		self.rootMenuItem = gui.mainFrame.sysTrayIcon.menu.Insert(2, wx.ID_ANY, _("English Reading Enhancer"), self.rootMenu)

	def updateCheckToggleString(self):
		return _("Disable checking for updates on startup") if self.getUpdateCheckSetting() is True else _("Enable checking for updates on startup")

	def toggleUpdateCheck(self, evt):
		changed = not self.getUpdateCheckSetting()
		self.setUpdateCheckSetting(changed)
		msg = _("Updates will be checked automatically when launching NVDA.") if changed is True else _("Updates will not be checked when launching NVDA.")
		self.updateCheckToggleItem.SetItemLabel(self.updateCheckToggleString())
		gui.messageBox(msg, _("Settings changed"))

	def performUpdateCheck(self, evt):
		updater.AutoUpdateChecker().autoUpdateCheck(mode=updater.MANUAL)

	def getUpdateCheckSetting(self):
		return config.conf["ERE_global"]["checkForUpdatesOnStartup"]

	def setUpdateCheckSetting(self, val):
		config.conf["ERE_global"]["checkForUpdatesOnStartup"] = val

	def toggleState(self, evt):
		changed = not self.getStateSetting()
		self.setStateSetting(changed)
		msg = _("English Reading Enhancer has been enabled.") if changed is True else _("English Reading Enhancer has been disabled.")
		self.stateToggleItem.SetItemLabel(self.stateToggleString())
		gui.messageBox(msg, _("Settings changed"))
		if changed:
			t = threading.Thread(target=self._checkAutoLanguageSwitchingState, daemon=True)
			t.start()

	def getStateSetting(self):
		return config.conf["ERE_global"]["enable"]

	def setStateSetting(self, val):
		config.conf["ERE_global"]["enable"] = val
		if val:
			self._setup()
		else:
			self._unsetup()

	def stateToggleString(self):
		return _("Disable English Reading Enhancer") if self.getStateSetting() is True else _("Enable English Reading Enhancer")

