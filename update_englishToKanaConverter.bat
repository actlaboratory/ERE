@echo off
cd %~dp0
cd addon\globalPlugins\ERE\_englishToKanaConverter 
git checkout -q main
git pull -q
cd ..\..\..\..
git add addon\globalPlugins\ERE\_englishToKanaConverter 
git commit -m "update submodule"
