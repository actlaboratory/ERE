# coding: UTF-8

from __future__ import unicode_literals
import addonHandler, globalPluginHandler, globalVars, threading, time, wx
from logHandler import log
from .constants import *
from . import updater

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

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		self.autoUpdateChecker.terminate()
