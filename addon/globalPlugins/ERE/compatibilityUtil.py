import gui
import wx
import versionInfo

def isCompatibleWith2025():
    return versionInfo.version_year >= 2025

def messageBox(message: str, title: str, parent: wx.Window | None=None):
    if isCompatibleWith2025():
        gui.message.MessageDialog.alert(message, title, parent)
    else:
        gui.messageBox(message, title, style=wx.CENTER, parent=parent)
