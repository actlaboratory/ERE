# coding: UTF-8

"""開発中の辞書と、同梱されている既定の辞書とを実行時に切り替える。

englishToKanaConverter は辞書を ``dictionaries.PHRASES`` のようにモジュール属性として
参照している。参照は変換のたびに行われるため、この属性を差し替えるだけで、
NVDA を再起動することなく、その場で辞書を切り替えられる。

開発中の辞書は ``_devDictionaries`` ディレクトリに置く。ここに存在するファイルだけが
差し替えの対象になるので、変更のないファイルまで複製する必要はない。
ディレクトリごと存在しない場合は切り替え機能自体が無効になる。

辞書の更新には ``update_devDictionaries.bat`` を使う。
"""

import json
import os

from logHandler import log

from ._englishToKanaConverter.englishToKanaConverter import dictionaries

# _devDictionaries に置いたファイル名と、差し替える属性名の対応
_TARGETS = {
	"phrases": "PHRASES",
	"prefix": "PREFIX",
	"roman": "ROMAN",
	"spell": "SPELL",
	"suffix": "SUFFIX",
	"words": "WORDS",
}

_DEV_DIR = os.path.join(os.path.dirname(__file__), "_devDictionaries")

# 既定の辞書。最初に切り替える直前の状態を控えておき、元に戻す際に使う
_defaults = {}
# 開発中の辞書。一度読み込んだら保持する
_devCache = None


def isAvailable():
	"""開発中の辞書が同梱されているか。"""
	if not os.path.isdir(_DEV_DIR):
		return False
	return any(
		os.path.isfile(os.path.join(_DEV_DIR, "%s.json" % name))
		for name in _TARGETS
	)


def getDevDictionaryNames():
	"""開発中の辞書として同梱されているファイル名の一覧。"""
	if not os.path.isdir(_DEV_DIR):
		return []
	return sorted(
		name for name in _TARGETS
		if os.path.isfile(os.path.join(_DEV_DIR, "%s.json" % name))
	)


def _loadDev():
	global _devCache
	if _devCache is not None:
		return _devCache
	loaded = {}
	for name in getDevDictionaryNames():
		path = os.path.join(_DEV_DIR, "%s.json" % name)
		with open(path, encoding="utf-8") as f:
			loaded[name] = json.load(f)
	_devCache = loaded
	return _devCache


def _apply(source):
	for name, value in source.items():
		setattr(dictionaries, _TARGETS[name], value)


def useDev():
	"""開発中の辞書に切り替える。切り替えた辞書の件数を返す。"""
	dev = _loadDev()
	if not dev:
		raise RuntimeError("開発中の辞書が見つかりません。")
	# 最初の切り替え時にだけ、既定の辞書を控えておく
	for name in dev:
		if name not in _defaults:
			_defaults[name] = getattr(dictionaries, _TARGETS[name])
	_apply(dev)
	log.info("ERE: 開発中の辞書に切り替えました (%s)" % ", ".join(sorted(dev)))
	return {name: len(value) for name, value in dev.items()}


def useDefault():
	"""同梱されている既定の辞書に戻す。"""
	if not _defaults:
		# 一度も切り替えていないので、すでに既定の状態
		return {}
	_apply(_defaults)
	log.info("ERE: 既定の辞書に戻しました")
	return {name: len(value) for name, value in _defaults.items()}


def describe():
	"""現在使われている辞書の概要を、利用者に見せる文字列で返す。"""
	return "phrases.json: %d件, words.json: %d件" % (
		len(dictionaries.PHRASES), len(dictionaries.WORDS)
	)
