# coding: UTF-8
"""
Speech Hook Module for English Reading Enhancer

This module manages the integration between NVDA's speech system and
the extension point-based text processing pipeline.

Instead of directly monkey-patching speech.processText, this module
provides a clean interface that uses the extension point system.
"""

from __future__ import unicode_literals
from copy import deepcopy
from typing import Callable, Optional, Any, List
import speech
import speechDictHandler
from logHandler import log
from . import extensionPoints


class SpeechHookManager:
	"""
	Manages the speech hook lifecycle.

	This class handles:
	- Installing/uninstalling the speech processText hook
	- Managing speech dictionary modifications
	- Coordinating with the extension point system
	"""

	def __init__(self):
		self._originalProcessText: Optional[Callable] = None
		self._originalBuiltinDict: Optional[Any] = None
		self._isInstalled: bool = False
		self._enabled: bool = False

	@property
	def isInstalled(self) -> bool:
		"""Check if the speech hook is currently installed."""
		return self._isInstalled

	@property
	def isEnabled(self) -> bool:
		"""Check if text processing is enabled."""
		return self._enabled

	def setEnabled(self, enabled: bool) -> None:
		"""Enable or disable text processing (without uninstalling hook)."""
		self._enabled = enabled
		if enabled:
			extensionPoints.textProcessing.onEnabled.notify()
		else:
			extensionPoints.textProcessing.onDisabled.notify()

	def install(self) -> None:
		"""
		Install the speech hook.

		This replaces NVDA's processText with our wrapper that uses
		the extension point system.
		"""
		if self._isInstalled:
			log.debug("SpeechHookManager: Hook already installed")
			return

		# Store original processText
		if hasattr(speech, "speech"):
			self._originalProcessText = speech.speech.processText
		else:
			self._originalProcessText = speech.processText

		# Create wrapper function
		def processText(locale: str, text: str, symbolLevel, **kwargs) -> str:
			# Apply pre-processing filters only if enabled
			if self._enabled:
				text = extensionPoints.textProcessing.preProcessText.apply(
					text, locale=locale, symbolLevel=symbolLevel
				)

			# Call original NVDA processText
			text = self._originalProcessText(locale, text, symbolLevel, **kwargs)

			# Apply post-processing filters only if enabled
			if self._enabled:
				text = extensionPoints.textProcessing.postProcessText.apply(
					text, locale=locale, symbolLevel=symbolLevel
				)

			return text

		# Install the wrapper
		if hasattr(speech, "speech"):
			speech.speech.processText = processText
		else:
			speech.processText = processText

		self._isInstalled = True
		log.debug("SpeechHookManager: Hook installed")

	def uninstall(self) -> None:
		"""
		Uninstall the speech hook.

		This restores NVDA's original processText function.
		"""
		if not self._isInstalled:
			log.debug("SpeechHookManager: Hook not installed")
			return

		if self._originalProcessText is not None:
			if hasattr(speech, "speech"):
				speech.speech.processText = self._originalProcessText
			else:
				speech.processText = self._originalProcessText

		self._isInstalled = False
		self._originalProcessText = None
		log.debug("SpeechHookManager: Hook uninstalled")

	def applyDictionaryModifications(self) -> None:
		"""
		Apply speech dictionary modifications based on registered patterns.
		"""
		modifications = extensionPoints.speechDictModifier.getModifications()
		if not modifications:
			return

		# Store original state
		self._originalBuiltinDict = deepcopy(speechDictHandler.dictionaries["builtin"])
		extensionPoints.speechDictModifier.setOriginalState(self._originalBuiltinDict)

		# Apply modifications
		entriesToRemove: List[Any] = []
		for mod in modifications:
			if mod['type'] == 'remove_pattern':
				for entry in speechDictHandler.dictionaries["builtin"]:
					if entry.pattern == mod['pattern']:
						entriesToRemove.append(entry)

		for entry in entriesToRemove:
			try:
				index = speechDictHandler.dictionaries["builtin"].index(entry)
				del speechDictHandler.dictionaries["builtin"][index]
				log.debug(f"Removed dictionary pattern: {entry.pattern}")
			except (ValueError, IndexError) as e:
				log.warning(f"Could not remove dictionary pattern: {e}")

	def restoreDictionaryModifications(self) -> None:
		"""
		Restore the original speech dictionary state.
		"""
		originalState = extensionPoints.speechDictModifier.getOriginalState()
		if originalState is not None:
			speechDictHandler.dictionaries["builtin"] = originalState
			extensionPoints.speechDictModifier.setOriginalState(None)
			log.debug("SpeechHookManager: Dictionary restored")


# Global singleton instance
_manager: Optional[SpeechHookManager] = None


def getManager() -> SpeechHookManager:
	"""Get the global SpeechHookManager instance."""
	global _manager
	if _manager is None:
		_manager = SpeechHookManager()
	return _manager


def registerDefaultPatternRemovals() -> None:
	"""Register the default patterns to be removed from the builtin dictionary."""
	# These patterns are removed because they interfere with English text processing
	# on Japanese synthesizers (e.g., camelCase word splitting)
	extensionPoints.speechDictModifier.registerPatternRemoval("([a-z])([A-Z])")
	extensionPoints.speechDictModifier.registerPatternRemoval("([A-Z])([A-Z][a-z])")
