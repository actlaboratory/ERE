# coding: UTF-8

from __future__ import unicode_literals
import addonHandler, globalPluginHandler, globalVars, threading, time, wx
import speech
from logHandler import log
from .constants import *
from . import updater
from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter

try:
	import addonHandler
	addonHandler.initTranslation()
except:
	_ = lambda x : x


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.autoUpdateChecker = updater.AutoUpdateChecker()
		self.autoUpdateChecker.autoUpdateCheck()
		self._setup()

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		self.autoUpdateChecker.terminate()

	def _setup(self):
		if hasattr(speech, "speech"):
			processText_original = speech.speech.processText
		else:
			processText_original = speech.processText
		c = EnglishToKanaConverter()

		def processText(locale, text, symbolLevel):
			text = processText_original(locale, text, symbolLevel)
			if locale.startswith("ja"):
				text = c.process(text)
			return text
		if hasattr(speech, "speech"):
			speech.speech.processText = processText
		else:
			speech.processText = processText
