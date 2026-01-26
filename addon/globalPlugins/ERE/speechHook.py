# coding: UTF-8
"""
English Reading Enhancer用の音声フックモジュール

このモジュールは、NVDAの音声システムと
拡張ポイントベースのテキスト処理パイプライン間の統合を管理する。

speech.processTextを直接モンキーパッチする代わりに、
このモジュールは拡張ポイントシステムを使用するクリーンなインターフェースを提供する。
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
	音声フックのライフサイクルを管理する。

	このクラスは以下を処理する:
	- speech processTextフックのインストール/アンインストール
	- 音声辞書の変更の管理
	- 拡張ポイントシステムとの連携
	"""

	def __init__(self):
		self._originalProcessText: Optional[Callable] = None
		self._originalBuiltinDict: Optional[Any] = None
		self._isInstalled: bool = False
		self._enabled: bool = False

	@property
	def isInstalled(self) -> bool:
		"""音声フックが現在インストールされているか確認する。"""
		return self._isInstalled

	@property
	def isEnabled(self) -> bool:
		"""テキスト処理が有効か確認する。"""
		return self._enabled

	def setEnabled(self, enabled: bool) -> None:
		"""テキスト処理を有効/無効にする（フックのアンインストールなし）。"""
		self._enabled = enabled
		if enabled:
			extensionPoints.textProcessing.onEnabled.notify()
		else:
			extensionPoints.textProcessing.onDisabled.notify()

	def install(self) -> None:
		"""
		音声フックをインストールする。

		NVDAのprocessTextを拡張ポイントシステムを使用する
		ラッパーに置き換える。
		"""
		if self._isInstalled:
			log.debug("SpeechHookManager: Hook already installed")
			return

		# 元のprocessTextを保存
		if hasattr(speech, "speech"):
			self._originalProcessText = speech.speech.processText
		else:
			self._originalProcessText = speech.processText

		# ラッパー関数を作成
		def processText(locale: str, text: str, symbolLevel, **kwargs) -> str:
			# 有効な場合のみ前処理フィルタを適用
			if self._enabled:
				text = extensionPoints.textProcessing.preProcessText.apply(
					text, locale=locale, symbolLevel=symbolLevel
				)

			# 元のNVDA processTextを呼び出す
			text = self._originalProcessText(locale, text, symbolLevel, **kwargs)

			# 有効な場合のみ後処理フィルタを適用
			if self._enabled:
				text = extensionPoints.textProcessing.postProcessText.apply(
					text, locale=locale, symbolLevel=symbolLevel
				)

			return text

		# ラッパーをインストール
		if hasattr(speech, "speech"):
			speech.speech.processText = processText
		else:
			speech.processText = processText

		self._isInstalled = True
		log.debug("SpeechHookManager: Hook installed")

	def uninstall(self) -> None:
		"""
		音声フックをアンインストールする。

		NVDAの元のprocessText関数を復元する。
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
		登録されたパターンに基づいて音声辞書の変更を適用する。
		"""
		modifications = extensionPoints.speechDictModifier.getModifications()
		if not modifications:
			return

		# 元の状態を保存
		self._originalBuiltinDict = deepcopy(speechDictHandler.dictionaries["builtin"])
		extensionPoints.speechDictModifier.setOriginalState(self._originalBuiltinDict)

		# 変更を適用
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
		元の音声辞書の状態を復元する。
		"""
		originalState = extensionPoints.speechDictModifier.getOriginalState()
		if originalState is not None:
			speechDictHandler.dictionaries["builtin"] = originalState
			extensionPoints.speechDictModifier.setOriginalState(None)
			log.debug("SpeechHookManager: Dictionary restored")


# グローバルシングルトンインスタンス
_manager: Optional[SpeechHookManager] = None


def getManager() -> SpeechHookManager:
	"""グローバルなSpeechHookManagerインスタンスを取得する。"""
	global _manager
	if _manager is None:
		_manager = SpeechHookManager()
	return _manager


def registerDefaultPatternRemovals() -> None:
	"""組み込み辞書から削除するデフォルトのパターンを登録する。"""
	# これらのパターンは、日本語合成器での英語テキスト処理を妨げるため削除される
	# （例：キャメルケースの単語分割）
	extensionPoints.speechDictModifier.registerPatternRemoval("([a-z])([A-Z])")
	extensionPoints.speechDictModifier.registerPatternRemoval("([A-Z])([A-Z][a-z])")
