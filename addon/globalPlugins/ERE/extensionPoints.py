# coding: UTF-8
"""
Extension Points Module for English Reading Enhancer

This module provides extension point infrastructure for text processing,
allowing handlers to be registered and called in a clean, decoupled manner
instead of using function overrides/monkey-patching.

Extension point types:
- Filter: Allows handlers to modify data passing through
- Action: Notifies handlers when something happens (no return value)
"""

from __future__ import unicode_literals
from typing import Callable, List, Any, Optional
from logHandler import log


class HandlerRegistrar:
	"""Base class for managing handler registration."""

	def __init__(self):
		self._handlers: List[Callable] = []

	def register(self, handler: Callable) -> None:
		"""Register a handler function."""
		if handler not in self._handlers:
			self._handlers.append(handler)
			log.debug(f"Handler registered: {handler.__name__ if hasattr(handler, '__name__') else handler}")

	def unregister(self, handler: Callable) -> None:
		"""Unregister a handler function."""
		if handler in self._handlers:
			self._handlers.remove(handler)
			log.debug(f"Handler unregistered: {handler.__name__ if hasattr(handler, '__name__') else handler}")

	def isRegistered(self, handler: Callable) -> bool:
		"""Check if a handler is registered."""
		return handler in self._handlers

	@property
	def handlers(self) -> List[Callable]:
		"""Get list of registered handlers (copy)."""
		return self._handlers.copy()


class Filter(HandlerRegistrar):
	"""
	Extension point that allows handlers to filter/modify data.

	Handlers are called in registration order, each receiving the output
	of the previous handler. This creates a processing pipeline.

	Usage:
		textFilter = Filter()
		textFilter.register(my_handler)
		result = textFilter.apply(initial_value, locale="ja")
	"""

	def apply(self, value: Any, **kwargs) -> Any:
		"""
		Apply all registered handlers to the value.

		Args:
			value: The initial value to be filtered
			**kwargs: Additional keyword arguments passed to all handlers

		Returns:
			The filtered value after all handlers have processed it
		"""
		for handler in self._handlers:
			try:
				value = handler(value, **kwargs)
			except Exception as e:
				log.error(f"Error in filter handler {handler}: {e}")
		return value


class Action(HandlerRegistrar):
	"""
	Extension point that notifies handlers when an event occurs.

	Unlike Filter, handlers don't return values - they just receive
	notification that something happened.

	Usage:
		onEnabled = Action()
		onEnabled.register(my_handler)
		onEnabled.notify(some_data="value")
	"""

	def notify(self, **kwargs) -> None:
		"""
		Notify all registered handlers.

		Args:
			**kwargs: Keyword arguments passed to all handlers
		"""
		for handler in self._handlers:
			try:
				handler(**kwargs)
			except Exception as e:
				log.error(f"Error in action handler {handler}: {e}")


class TextProcessingExtensionPoint:
	"""
	Extension point for text processing before speech synthesis.

	This replaces the previous monkey-patching approach with a clean
	extension point that allows text processors to be registered
	and applied in sequence.
	"""

	# Filter applied before NVDA's processText
	preProcessText = Filter()

	# Filter applied after NVDA's processText
	postProcessText = Filter()

	# Action triggered when processing is enabled
	onEnabled = Action()

	# Action triggered when processing is disabled
	onDisabled = Action()


class SpeechDictModifier:
	"""
	Extension point for modifying speech dictionaries.

	Provides a clean interface for registering dictionary modifications
	that can be applied/reverted without direct manipulation.
	"""

	def __init__(self):
		self._modifications: List[dict] = []
		self._originalState: Optional[Any] = None

	def registerPatternRemoval(self, pattern: str) -> None:
		"""Register a pattern to be removed from builtin dictionary."""
		self._modifications.append({
			'type': 'remove_pattern',
			'pattern': pattern
		})

	def getModifications(self) -> List[dict]:
		"""Get list of registered modifications."""
		return self._modifications.copy()

	def setOriginalState(self, state: Any) -> None:
		"""Store the original dictionary state for restoration."""
		self._originalState = state

	def getOriginalState(self) -> Optional[Any]:
		"""Get the stored original state."""
		return self._originalState


# Global extension point instances
textProcessing = TextProcessingExtensionPoint()
speechDictModifier = SpeechDictModifier()


def resetAll() -> None:
	"""Reset all extension points (useful for testing or cleanup)."""
	textProcessing.preProcessText._handlers.clear()
	textProcessing.postProcessText._handlers.clear()
	textProcessing.onEnabled._handlers.clear()
	textProcessing.onDisabled._handlers.clear()
	speechDictModifier._modifications.clear()
	speechDictModifier._originalState = None
