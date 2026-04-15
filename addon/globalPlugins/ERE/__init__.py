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
from . import compatibilityUtil
from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter
from scriptHandler import script

try:
	import addonHandler
	addonHandler.initTranslation()
except:
	_ = lambda x : x


confspec = {
	"checkForUpdatesOnStartup": "boolean(default=True)",
	"enable": "boolean(default=True)",
	"accessToken": 'string(default="")'
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
			compatibilityUtil.messageBox(_("Automatic Language switching is enabled. English Reading Enhancer may not work correctly. To use this add-on, we recommend to disable this functionality."), _("Warning"))

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

		def processText(locale, text, symbolLevel, **kwargs):
			# 2026/01/11 本家のprocessTextよりも前にカナ変換をするように変更
			# 従来の実装ではアポストロフィーなどの記号が読みに変換されたあとで処理されるため、「haven't」などが正しく読めなかった
			if locale.startswith("ja") and self.getStateSetting():
				text = c.process(text)
			text = self.processText_original(locale, text, symbolLevel, **kwargs)
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
		# github issues
		self.ghMenu = wx.Menu()
		self.reportMisreadingsItem = self.ghMenu.Append(wx.ID_ANY, _("Report Misreadings") + "...", _("Report words that cannot be read correctly in English Reading Enhancer."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.reportMisreadings, self.reportMisreadingsItem)
		self.setAccessTokenItem = self.ghMenu.Append(wx.ID_ANY, _("Set GitHub Access Token") + "...", _("Enter your personal GitHub access token."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.setAccessToken, self.setAccessTokenItem)
		self.openIssuesListItem = self.ghMenu.Append(wx.ID_ANY, _("Open Report List"), _("Open the list of received reports in your browser."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.openIssuesList, self.openIssuesListItem)
		self.ghMenuItem = self.rootMenu.Append(wx.ID_ANY, _("Report Misreadings"), self.ghMenu)
		self.rootMenuItem = gui.mainFrame.sysTrayIcon.menu.Insert(2, wx.ID_ANY, _("English Reading Enhancer"), self.rootMenu)

	def updateCheckToggleString(self):
		return _("Disable checking for updates on startup") if self.getUpdateCheckSetting() is True else _("Enable checking for updates on startup")

	def toggleUpdateCheck(self, evt):
		changed = not self.getUpdateCheckSetting()
		self.setUpdateCheckSetting(changed)
		msg = _("Updates will be checked automatically when launching NVDA.") if changed is True else _("Updates will not be checked when launching NVDA.")
		self.updateCheckToggleItem.SetItemLabel(self.updateCheckToggleString())
		compatibilityUtil.messageBox(msg, _("Settings changed"))

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
		compatibilityUtil.messageBox(msg, _("Settings changed"))
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

	# github issues
	def reportMisreadings(self, evt):
		# 多重起動防止
		if gui.message.isModalMessageBoxActive():
			return
		if not config.conf["ERE_global"]["accessToken"]:
			compatibilityUtil.messageBox(_("Before using this feature, please set your GitHub Access Token."), _("Error"))
			return
		from .dialogs import reportMisreadingsDialog
		gui.mainFrame.prePopup()
		dialog = reportMisreadingsDialog.ReportMisreadingsDialog(gui.mainFrame)
		res = gui.message.displayDialogAsModal(dialog)
		dialog.Destroy()
		gui.mainFrame.postPopup()
		if res == wx.ID_CANCEL:
			return
		# retrieve data from dialog
		eng = dialog.wordEdit.GetValue().strip()
		oldKana = EnglishToKanaConverter().process(eng)
		newKana = dialog.pronunciationEdit.GetValue().strip()
		comment = dialog.commentEdit.GetValue().strip()
		# validation
		z = zip(
			(_("Word"), _("Pronunciation")),
			(eng, newKana),
		)
		for label, field in z:
			if not field:
				compatibilityUtil.messageBox(_("%s is not entered.") % label, _("Error"))
				return
		# end validation
		from .constants import addonVersion
		self._sendMisreadings(eng, oldKana, newKana, comment, addonVersion)

	def _sendMisreadings(self, eng, oldKana, newKana, comment, addonVersion):
		# issue title/body(in Japanese)
		title = GH_ISSUE_PREFIX + eng
		body = f"""#### 単語

{eng}

#### 現在の読み方

{oldKana}

#### 新しい読み方

{newKana}

#### コメント

{comment}

#### アドオンのバージョン

{addonVersion}"""
		# send data
		from .ghUtil import GhUtil
		util = GhUtil(config.conf["ERE_global"]["accessToken"])
		result = util.createIssue(GH_REPO_OWNER, GH_REPO_NAME, title, body)
		if not result:
			compatibilityUtil.messageBox(_("Failed to send a report."), _("Error"))
			return
		compatibilityUtil.messageBox(_("Report sent."), _("Success"))

	# define script
	@script(description=_("Report Misreadings"), gesture="kb:nvda+control+shift+e")
	def script_reportMisreadings(self, gesture):
		wx.CallAfter(self.reportMisreadings, None)

	def setAccessToken(self, evt):
		if gui.message.isModalMessageBoxActive():
			return
		token = config.conf["ERE_global"]["accessToken"]
		# 正常な値が入力されるまで「ダイアログの表示→有効性確認」を続ける
		while True:
			gui.mainFrame.prePopup()
			d = wx.TextEntryDialog(gui.mainFrame, _("GitHub Access Token"), _("Set GitHub Access Token"), token)
			res = gui.message.displayDialogAsModal(d)
			d.Destroy()
			gui.mainFrame.postPopup()
			if res == wx.ID_CANCEL:
				# 何もせずにループも関数も抜ける
				return
			token = d.GetValue().strip()
			# 入力内容が空ならば、「設定値を削除した」と見なす
			if not token:
				break
			# 動作確認
			from .ghUtil import GhUtil
			util = GhUtil(token)
			if not util.isActive():
				# 認証されていない
				compatibilityUtil.messageBox(_("GitHub Access Token is invalid."), _("Error"))
				continue
			break
		config.conf["ERE_global"]["accessToken"] = token

	def openIssuesList(self, evt):
		from urllib.parse import quote
		url = f"https://github.com/{GH_REPO_OWNER}/{GH_REPO_NAME}/issues?q=is%3Aissue+" + quote(GH_ISSUE_PREFIX)
		os.startfile(url)
