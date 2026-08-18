# -*- coding: utf-8 -*-
# 動作検証用に、englishToKanaConverter の任意のブランチから辞書を取り出す

"""englishToKanaConverter の指定ブランチにある辞書を取り出し、
addon/globalPlugins/ERE/_devDictionaries に配置する。

    python tools/update_dev_dictionaries.py issue5-dictionary-policy

配置後にアドオンをビルドすると、NVDA のメニューに
「開発中の辞書に切り替え」という項目が現れ、その場で辞書を切り替えられる。

submodule のチェックアウト状態は変更しない。origin/main との差分がある辞書だけを
取り出すため、変更のないファイルまで複製されることはない。
切り替え機能ごと取り除きたい場合は、--clean を指定するか _devDictionaries を削除する。
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMODULE = os.path.join(ROOT, "addon", "globalPlugins", "ERE", "_englishToKanaConverter")
DEV_DIR = os.path.join(ROOT, "addon", "globalPlugins", "ERE", "_devDictionaries")
DICT_PATH = "englishToKanaConverter/dictionaries"


def git(*args):
	"""submodule 内で git を実行し、標準出力を返す。"""
	result = subprocess.run(
		["git"] + list(args),
		cwd=SUBMODULE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)
	if result.returncode != 0:
		raise RuntimeError(
			"git %s に失敗しました: %s"
			% (" ".join(args), result.stderr.decode("utf-8", "replace").strip())
		)
	return result.stdout


def clean():
	if not os.path.isdir(DEV_DIR):
		print("_devDictionaries は存在しません。")
		return
	for name in os.listdir(DEV_DIR):
		os.remove(os.path.join(DEV_DIR, name))
	os.rmdir(DEV_DIR)
	print("_devDictionaries を削除しました。切り替え項目は表示されなくなります。")


def update(branch):
	if not os.path.isdir(SUBMODULE):
		raise RuntimeError(
			"submodule が見つかりません。git submodule update --init を実行してください。"
		)
	print("origin から取得しています...")
	git("fetch", "-q", "origin")

	try:
		git("rev-parse", "--verify", "-q", "origin/%s" % branch)
	except RuntimeError:
		branches = git("branch", "-r", "--format=%(refname:short)")
		print('ブランチ "%s" が origin に見つかりません。' % branch, file=sys.stderr)
		print("\n利用できるブランチ:", file=sys.stderr)
		for line in branches.decode("utf-8").splitlines():
			print("  %s" % line.strip(), file=sys.stderr)
		return 1

	diff = git(
		"diff", "--name-only", "origin/main..origin/%s" % branch, "--", DICT_PATH
	).decode("utf-8").split()
	if not diff:
		print("origin/main と辞書の差分がありません。切り替える意味がないため、何も配置しませんでした。")
		clean()
		return 0

	if not os.path.isdir(DEV_DIR):
		os.makedirs(DEV_DIR)
	for name in os.listdir(DEV_DIR):
		os.remove(os.path.join(DEV_DIR, name))

	for path in diff:
		blob = git("show", "origin/%s:%s" % (branch, path))
		name = os.path.basename(path)
		dest = os.path.join(DEV_DIR, name)
		with open(dest, "wb") as f:
			f.write(blob)
		# 妥当な JSON かをここで確かめておく。壊れたものを NVDA に持ち込まないため
		with open(dest, encoding="utf-8") as f:
			entries = len(json.load(f))
		print("  %-16s %d件" % (name, entries))

	print("\n%d 個の辞書を配置しました (origin/%s)。" % (len(diff), branch))
	print("アドオンをビルドすると、NVDA のメニューに切り替え項目が現れます。")
	return 0


def main():
	parser = argparse.ArgumentParser(
		description="englishToKanaConverter の指定ブランチの辞書を、動作検証用に取り出す。"
	)
	parser.add_argument("branch", nargs="?", help="取り出すブランチ名")
	parser.add_argument(
		"--clean", action="store_true", help="_devDictionaries を削除し、切り替え機能を取り除く"
	)
	args = parser.parse_args()

	if args.clean:
		clean()
		return 0
	if not args.branch:
		parser.print_help()
		return 1
	return update(args.branch)


if __name__ == "__main__":
	try:
		sys.exit(main())
	except RuntimeError as e:
		print(e, file=sys.stderr)
		sys.exit(1)
