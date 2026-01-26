# coding: UTF-8
"""
English Reading Enhancer用のテキストプロセッサモジュール

このモジュールは、拡張ポイントシステムに登録できる
テキストプロセッサクラスを定義します。
"""

from __future__ import unicode_literals
from abc import ABC, abstractmethod
from typing import Optional
from logHandler import log


class TextProcessor(ABC):
	"""
	テキストプロセッサの抽象基底クラス。

	テキストプロセッサは、音声合成器に渡される前にテキストを変換する。
	各プロセッサはprocessメソッドを実装し、
	オプションでロケールによるフィルタリングができる。
	"""

	def __init__(self, localePrefix: Optional[str] = None):
		"""
		テキストプロセッサを初期化する。

		引数:
			localePrefix: 設定された場合、このプレフィックスで始まるロケールのテキストのみ処理する
		"""
		self._localePrefix = localePrefix

	@abstractmethod
	def process(self, text: str) -> str:
		"""
		指定されたテキストを処理する。

		引数:
			text: 処理する入力テキスト

		戻り値:
			処理されたテキスト
		"""
		pass

	def __call__(self, text: str, locale: str = "", **kwargs) -> str:
		"""
		プロセッサを拡張ポイントハンドラとして呼び出し可能にする。

		引数:
			text: 処理する入力テキスト
			locale: テキストのロケール
			**kwargs: 追加の引数（無視される）

		戻り値:
			処理されたテキスト、またはロケールが一致しない場合は元のテキスト
		"""
		if self._localePrefix and not locale.startswith(self._localePrefix):
			return text
		return self.process(text)


class EnglishToKanaProcessor(TextProcessor):
	"""
	日本語音声合成器用に英語テキストをカナに変換するテキストプロセッサ。

	このプロセッサはEnglishToKanaConverterをラップし、
	拡張ポイントシステムに登録する。
	"""

	def __init__(self):
		super().__init__(localePrefix="ja")
		self._converter = None

	def _getConverter(self):
		"""コンバータの遅延初期化。"""
		if self._converter is None:
			from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter
			self._converter = EnglishToKanaConverter()
		return self._converter

	def process(self, text: str) -> str:
		"""
		テキスト内の英単語をカナに変換する。

		引数:
			text: 英単語を含む可能性のある入力テキスト

		戻り値:
			英単語がカナに変換されたテキスト
		"""
		try:
			return self._getConverter().process(text)
		except Exception as e:
			log.error(f"EnglishToKanaProcessor error: {e}")
			return text


# EnglishToKanaプロセッサのシングルトンインスタンス
_englishToKanaProcessor: Optional[EnglishToKanaProcessor] = None


def getEnglishToKanaProcessor() -> EnglishToKanaProcessor:
	"""シングルトンのEnglishToKanaProcessorインスタンスを取得する。"""
	global _englishToKanaProcessor
	if _englishToKanaProcessor is None:
		_englishToKanaProcessor = EnglishToKanaProcessor()
	return _englishToKanaProcessor
