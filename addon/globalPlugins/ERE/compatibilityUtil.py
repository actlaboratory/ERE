import gui
import wx
try:                                                                                                                   
    import buildVersion as _versionInfo                                                                                
except ImportError:                                                                                                    
    import versionInfo as _versionInfo                                                                                 
 
def isCompatibleWith2025():
    return _versionInfo.version_year >= 2025

def messageBox(message: str, title: str, parent: wx.Window | None=None):
    if isCompatibleWith2025():
        gui.message.MessageDialog.alert(message, title, parent)
    else:
        gui.messageBox(message, title, style=wx.CENTER, parent=parent)
