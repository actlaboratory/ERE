# coding: UTF-8
"""
English Reading Enhancer用の拡張ポイントモジュール

このモジュールは、関数オーバーライド/モンキーパッチの代わりに、
ハンドラを登録して呼び出すためのクリーンで疎結合な
テキスト処理用の拡張ポイント基盤を提供します。

拡張ポイントの種類:
- Filter: ハンドラがデータを変更できるようにする
- Action: 何かが起きた時にハンドラに通知する（戻り値なし）
"""

from __future__ import unicode_literals
from typing import Callable, List, Any, Optional
from logHandler import log


class HandlerRegistrar:
	"""ハンドラ登録を管理する基底クラス。"""

	def __init__(self):
		self._handlers: List[Callable] = []

	def register(self, handler: Callable) -> None:
		"""ハンドラ関数を登録する。"""
		if handler not in self._handlers:
			self._handlers.append(handler)
			log.debug(f"Handler registered: {handler.__name__ if hasattr(handler, '__name__') else handler}")

	def unregister(self, handler: Callable) -> None:
		"""ハンドラ関数の登録を解除する。"""
		if handler in self._handlers:
			self._handlers.remove(handler)
			log.debug(f"Handler unregistered: {handler.__name__ if hasattr(handler, '__name__') else handler}")

	def isRegistered(self, handler: Callable) -> bool:
		"""ハンドラが登録されているか確認する。"""
		return handler in self._handlers

	@property
	def handlers(self) -> List[Callable]:
		"""登録されているハンドラのリスト（コピー）を取得する。"""
		return self._handlers.copy()


class Filter(HandlerRegistrar):
	"""
	ハンドラがデータをフィルタ/変更できる拡張ポイント。

	ハンドラは登録順に呼び出され、それぞれが前のハンドラの出力を受け取る。
	これにより処理パイプラインが作成される。

	使用例:
		textFilter = Filter()
		textFilter.register(my_handler)
		result = textFilter.apply(initial_value, locale="ja")
	"""

	def apply(self, value: Any, **kwargs) -> Any:
		"""
		登録されているすべてのハンドラを値に適用する。

		引数:
			value: フィルタリングする初期値
			**kwargs: すべてのハンドラに渡される追加のキーワード引数

		戻り値:
			すべてのハンドラが処理した後のフィルタリングされた値
		"""
		for handler in self._handlers:
			try:
				value = handler(value, **kwargs)
			except Exception as e:
				log.error(f"Error in filter handler {handler}: {e}")
		return value


class Action(HandlerRegistrar):
	"""
	イベント発生時にハンドラに通知する拡張ポイント。

	Filterとは異なり、ハンドラは値を返さない。
	何かが起きたという通知を受け取るだけ。

	使用例:
		onEnabled = Action()
		onEnabled.register(my_handler)
		onEnabled.notify(some_data="value")
	"""

	def notify(self, **kwargs) -> None:
		"""
		登録されているすべてのハンドラに通知する。

		引数:
			**kwargs: すべてのハンドラに渡されるキーワード引数
		"""
		for handler in self._handlers:
			try:
				handler(**kwargs)
			except Exception as e:
				log.error(f"Error in action handler {handler}: {e}")


class TextProcessingExtensionPoint:
	"""
	音声合成前のテキスト処理用の拡張ポイント。

	以前のモンキーパッチ方式を、テキストプロセッサを登録して
	順番に適用できるクリーンな拡張ポイントに置き換える。
	"""

	# NVDAのprocessTextの前に適用されるフィルタ
	preProcessText = Filter()

	# NVDAのprocessTextの後に適用されるフィルタ
	postProcessText = Filter()

	# 処理が有効になった時にトリガーされるアクション
	onEnabled = Action()

	# 処理が無効になった時にトリガーされるアクション
	onDisabled = Action()


class SpeechDictModifier:
	"""
	音声辞書を変更するための拡張ポイント。

	直接操作せずに適用/元に戻すことができる
	辞書変更を登録するためのクリーンなインターフェースを提供する。
	"""

	def __init__(self):
		self._modifications: List[dict] = []
		self._originalState: Optional[Any] = None

	def registerPatternRemoval(self, pattern: str) -> None:
		"""組み込み辞書から削除するパターンを登録する。"""
		self._modifications.append({
			'type': 'remove_pattern',
			'pattern': pattern
		})

	def getModifications(self) -> List[dict]:
		"""登録されている変更のリストを取得する。"""
		return self._modifications.copy()

	def setOriginalState(self, state: Any) -> None:
		"""復元用に元の辞書状態を保存する。"""
		self._originalState = state

	def getOriginalState(self) -> Optional[Any]:
		"""保存されている元の状態を取得する。"""
		return self._originalState


# グローバル拡張ポイントインスタンス
textProcessing = TextProcessingExtensionPoint()
speechDictModifier = SpeechDictModifier()


def resetAll() -> None:
	"""すべての拡張ポイントをリセットする（テストやクリーンアップに便利）。"""
	textProcessing.preProcessText._handlers.clear()
	textProcessing.postProcessText._handlers.clear()
	textProcessing.onEnabled._handlers.clear()
	textProcessing.onDisabled._handlers.clear()
	speechDictModifier._modifications.clear()
	speechDictModifier._originalState = None
