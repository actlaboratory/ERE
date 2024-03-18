# -*- coding: UTF-8 -*-

import wx

# 翻訳が当たるようにする
try:
	import addonHandler
	addonHandler.initTranslation()
except:
	_ = lambda x : x

class ReportMisreadingsDialog(wx.Dialog):
	def __init__(self, *args, **kwds):
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetTitle(_("Report Misreadings"))

		vSizer = wx.BoxSizer(wx.VERTICAL)

		gridSizer = wx.GridSizer(3, 2, 10, 10)
		vSizer.Add(gridSizer, 1, wx.EXPAND, 0)

		wordLabel = wx.StaticText(self, wx.ID_ANY, _("Word"))
		gridSizer.Add(wordLabel, 0, 0, 0)

		self.wordEdit = wx.TextCtrl(self, wx.ID_ANY, "")
		gridSizer.Add(self.wordEdit, 0, 0, 0)

		pronunciationLabel = wx.StaticText(self, wx.ID_ANY, _("Pronunciation"))
		gridSizer.Add(pronunciationLabel, 0, 0, 0)

		self.pronunciationEdit = wx.TextCtrl(self, wx.ID_ANY, "")
		gridSizer.Add(self.pronunciationEdit, 0, 0, 0)

		commentLabel = wx.StaticText(self, wx.ID_ANY, _("Comment"))
		gridSizer.Add(commentLabel, 0, 0, 0)

		self.commentEdit = wx.TextCtrl(self, wx.ID_ANY, "")
		gridSizer.Add(self.commentEdit, 0, 0, 0)

		buttonsSizer = wx.StdDialogButtonSizer()
		vSizer.Add(buttonsSizer, 0, wx.ALL, 4)

		self.okButton = wx.Button(self, wx.ID_OK, "")
		self.okButton.SetDefault()
		self.okButton.Bind(wx.EVT_BUTTON, self.okButtonPressedEvent)
		buttonsSizer.AddButton(self.okButton)

		self.cancelButton = wx.Button(self, wx.ID_CANCEL, "")
		buttonsSizer.AddButton(self.cancelButton)

		buttonsSizer.Realize()

		self.SetSizer(vSizer)
		vSizer.Fit(self)

		self.SetAffirmativeId(self.okButton.GetId())
		self.SetEscapeId(self.cancelButton.GetId())

		self.Layout()

	def okButtonPressedEvent(self, event: wx.CommandEvent):
		# validation
		z = zip(
			(_("Word"), _("Pronunciation")),
			(self.wordEdit.GetValue().strip(), self.pronunciationEdit.GetValue().strip()),
		)
		for label, field in z:
			if not field:
				import gui
				gui.messageBox(_("%s is not entered.") % label, _("Error"), wx.ICON_ERROR, self)
				return
		# end validation
		event.Skip()
