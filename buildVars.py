# -*- coding: UTF-8 -*-

import os

ADDON_VERSION = "1.1.3"
ADDON_RELEASE_DATE = "2026-04-15"
ADDON_NAME = "EnglishReadingEnhancer"
ADDON_KEYWORD = "ERE"


# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.


# Since some strings in `addon_info` are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the `_` function.
# To avoid initializing translations in this module we simply roll our own "fake" `_` function
# which returns whatever is given to it as an argument.
def _(arg):
	return arg


# Add-on information variables
addon_info = {
	# add-on Name/identifier, internal for NVDA
	"addon_name": ADDON_NAME,
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on
	# to be shown on installation and add-on information found in Add-ons Manager.
	"addon_summary": _("English Reading Enhancer"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description": _("This add-on improves quality of English reading on Japanese speech synthesizers. See add-on's help for details."),
	# version
	"addon_version": ADDON_VERSION,
	# Author(s)
	"addon_author": "Kazto Kitabatake - ACT Laboratory <support@actlab.org>",
	# URL for the add-on documentation support
	"addon_url": "https://actlab.org/software/ERE",
	# Documentation file name
	"addon_docFileName": "readme.html",
	# Minimum NVDA version supported (e.g. "2018.3.0", minor version is optional)
	"addon_minimumNVDAVersion": "2019.3",
	# Last NVDA version supported/tested (e.g. "2018.4.0", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion": "2026.1",
	# Add-on update channel (default is None, denoting stable releases,
	# and for development releases, use "dev".)
	# Do not change unless you know what you are doing!
	"addon_updateChannel": None,
}

# Define the python files that are the sources of your add-on.
# You can either list every file (using ""/") as a path separator,
# or use glob expressions.
# For example to include all files with a ".py" extension from the "globalPlugins" dir of your add-on
# the list can be written as follows:
# pythonSources = ["addon/globalPlugins/*.py"]
# For more information on SCons Glob expressions please take a look at:
# https://scons.org/doc/production/HTML/scons-user/apd.html
pythonSources = ["addon/globalPlugins/ERE/*.py", "addon/globalPlugins/ERE/dialogs/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = ["globalPlugins/ERE/_englishToKanaConverter/englishToKanaConverter/englishToKanaConverter.log"]

# 開発用の辞書（_devDictionaries）は動作検証のためのものなので、
# スナップショット版には含めてよいが、正式リリース版には含めない。
# TAG_NAME はタグからのリリースビルドでのみ設定される
# （.github/workflows/testAndBuild.yml の「Set tag name if This is an official release」）。
# スナップショットのビルドでは設定されないため、そちらには従来通り含まれる。
# 何らかの理由でこのディレクトリがリリース対象のブランチに入り込んでいても、
# 正式リリースのパッケージからは確実に取り除かれる。
_DEV_DICTIONARIES = os.path.join("addon", "globalPlugins", "ERE", "_devDictionaries")
if os.environ.get("TAG_NAME") and os.path.isdir(_DEV_DICTIONARIES):
	_devDictionaryFiles = sorted(os.listdir(_DEV_DICTIONARIES))
	for _name in _devDictionaryFiles:
		excludedFiles.append(os.path.join("globalPlugins", "ERE", "_devDictionaries", _name))
	print(
		"buildVars: 正式リリースのビルドのため、開発用の辞書 %d 件をパッケージから除外します: %s"
		% (len(_devDictionaryFiles), ", ".join(_devDictionaryFiles))
	)

# Base language for the NVDA add-on
# If your add-on is written in a language other than english, modify this variable.
# For example, set baseLanguage to "es" if your add-on is primarily written in spanish.
baseLanguage = "en"

# Markdown extensions for add-on documentation
# Most add-ons do not require additional Markdown extensions.
# If you need to add support for markup such as tables, fill out the below list.
# Extensions string must be of the form "markdown.extensions.extensionName"
# e.g. "markdown.extensions.tables" to add tables.
markdownExtensions = []
