# coding: UTF-8
"""
Text Processors Module for English Reading Enhancer

This module defines text processor classes that can be registered
with the extension point system for text processing.
"""

from __future__ import unicode_literals
from abc import ABC, abstractmethod
from typing import Optional
from logHandler import log


class TextProcessor(ABC):
	"""
	Abstract base class for text processors.

	Text processors transform text before it is passed to the speech
	synthesizer. Each processor should implement the process method
	and can optionally filter by locale.
	"""

	def __init__(self, localePrefix: Optional[str] = None):
		"""
		Initialize the text processor.

		Args:
			localePrefix: If set, only process text for locales starting with this prefix
		"""
		self._localePrefix = localePrefix

	@abstractmethod
	def process(self, text: str) -> str:
		"""
		Process the given text.

		Args:
			text: The input text to process

		Returns:
			The processed text
		"""
		pass

	def __call__(self, text: str, locale: str = "", **kwargs) -> str:
		"""
		Make the processor callable for use as an extension point handler.

		Args:
			text: The input text to process
			locale: The locale of the text
			**kwargs: Additional arguments (ignored)

		Returns:
			The processed text, or original text if locale doesn't match
		"""
		if self._localePrefix and not locale.startswith(self._localePrefix):
			return text
		return self.process(text)


class EnglishToKanaProcessor(TextProcessor):
	"""
	Text processor that converts English text to Kana for Japanese speech synthesizers.

	This processor wraps the EnglishToKanaConverter and registers it with
	the extension point system.
	"""

	def __init__(self):
		super().__init__(localePrefix="ja")
		self._converter = None

	def _getConverter(self):
		"""Lazy initialization of the converter."""
		if self._converter is None:
			from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter
			self._converter = EnglishToKanaConverter()
		return self._converter

	def process(self, text: str) -> str:
		"""
		Convert English words in the text to Kana.

		Args:
			text: The input text potentially containing English words

		Returns:
			Text with English words converted to Kana
		"""
		try:
			return self._getConverter().process(text)
		except Exception as e:
			log.error(f"EnglishToKanaProcessor error: {e}")
			return text


# Singleton instance for the English to Kana processor
_englishToKanaProcessor: Optional[EnglishToKanaProcessor] = None


def getEnglishToKanaProcessor() -> EnglishToKanaProcessor:
	"""Get the singleton EnglishToKanaProcessor instance."""
	global _englishToKanaProcessor
	if _englishToKanaProcessor is None:
		_englishToKanaProcessor = EnglishToKanaProcessor()
	return _englishToKanaProcessor
