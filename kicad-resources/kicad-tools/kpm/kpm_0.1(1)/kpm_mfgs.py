#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re
import kpm_db
import kpm_common
import kpm_config

sqlmfgsfields = [
  'id', 
  'shortname', 
  'fullname', 
  'www',
  'address',
  'note'
]

# ---------------------------------------------------------
# ManufacturerDialog
# ---------------------------------------------------------

class ManufacturerDialog(wx.Dialog):
  def __init__(self, parent, title, shortname="", fullname="", www="", address="", note=""):
    wx.Dialog.__init__(self, parent, title=title, size=(250,200))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(6,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.shortnametext = wx.StaticText(self, label="Short name")
    self.gridsizer.Add(self.shortnametext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.shortname = wx.TextCtrl(self, -1, size=(300,25))
    self.shortname.SetValue(shortname)
    self.gridsizer.Add(self.shortname, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.fullnametext = wx.StaticText(self, label="Full name")
    self.gridsizer.Add(self.fullnametext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.fullname = wx.TextCtrl(self, -1, size=(300,25))
    self.fullname.SetValue(fullname)
    self.gridsizer.Add(self.fullname, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.wwwtext = wx.StaticText(self, label="WWW")
    self.gridsizer.Add(self.wwwtext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.www = wx.TextCtrl(self, -1, size=(300,25))
    self.www.SetValue(www)
    self.gridsizer.Add(self.www, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.addresstext = wx.StaticText(self, label="Address")
    self.gridsizer.Add(self.addresstext, 0, flag=wx.ALL, border=3)
    self.address = wx.TextCtrl(self, -1, size=(300,100), style=wx.TE_MULTILINE)
    self.address.SetValue(address)
    self.gridsizer.Add(self.address, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.notetext = wx.StaticText(self, label="Note")
    self.gridsizer.Add(self.notetext, 0, flag=wx.ALL, border=3)
    self.note = wx.TextCtrl(self, -1, size=(300,100), style=wx.TE_MULTILINE)
    self.note.SetValue(note)
    self.gridsizer.Add(self.note, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()
   
# ---------------------------------------------------------
# Manufacturers Frame
# ---------------------------------------------------------

class ManufacturersFrame(wx.Dialog):
  def __init__(self, parent, title, shortname="", fullname="", www="", address="", note=""):
    wx.Dialog.__init__(self, parent, title=title, size=(800,500), style=wx.RESIZE_BORDER)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    id = wx.NewId()
    self.mfgs_ctrl = wx.ListCtrl(self, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER, size=(800,500))
    self.sizer.Add(self.mfgs_ctrl, 1, wx.ALL|wx.EXPAND)
    self.mfgs_ctrl.InsertColumn(0, 'ID', width=30)
    self.mfgs_ctrl.InsertColumn(1, 'Short name', width=80)
    self.mfgs_ctrl.InsertColumn(2, 'Full name', width=150)
    self.mfgs_ctrl.InsertColumn(3, 'WWW', width=150)
    self.mfgs_ctrl.InsertColumn(4, 'Address', width=150)
    self.mfgs_ctrl.InsertColumn(5, 'Note', width=200)
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.mfgs_ctrl)
    
    self.btnClose = wx.Button(self, wx.ID_CLOSE)
    self.btnAdd = wx.Button(self, wx.ID_NEW)
    self.btnEdit = wx.Button(self, wx.ID_EDIT)
    self.btnDelete = wx.Button(self, wx.ID_DELETE)

    self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.btnSizer.Add(self.btnAdd)
    self.btnSizer.Add(self.btnEdit)
    self.btnSizer.Add(self.btnDelete)
    self.btnSizer.Add(self.btnClose)

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()
    
    self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnClose)
    self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btnAdd)
    self.Bind(wx.EVT_BUTTON, self.OnEdit, self.btnEdit)
    self.Bind(wx.EVT_BUTTON, self.OnDelete, self.btnDelete)
    
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.UpdateManufacturers()
    self.selected_id = 0
    
  def UpdateManufacturers(self):
    mfgs = self.db.Select('mfgs', sqlmfgsfields)
    i = 0
    self.mfgs_ctrl.DeleteAllItems()
    for mfg in mfgs:
      self.mfgs_ctrl.InsertStringItem(i, str(mfg[0]))
      self.mfgs_ctrl.SetStringItem(i, 1, mfg[1])
      self.mfgs_ctrl.SetStringItem(i, 2, mfg[2])
      self.mfgs_ctrl.SetStringItem(i, 3, mfg[3])
      self.mfgs_ctrl.SetStringItem(i, 4, mfg[4])
      self.mfgs_ctrl.SetStringItem(i, 5, mfg[5])
      i+=1

  def OnSelect(self, event):
    item = event.GetItem()
    self.selected_id = int(item.GetText())
    #print(self.selected_id)
        
  def OnAdd(self,e):
    #print("new")
    newman = ManufacturerDialog(self, "New manufacturer")
    if newman.ShowModal() == wx.ID_OK:
      #print(newman.shortname.GetValue())
      fields = {}
      fields['shortname'] =  newman.shortname.GetValue()
      fields['fullname'] =  newman.fullname.GetValue()
      fields['www'] =  newman.www.GetValue()
      fields['address'] =  newman.address.GetValue()
      fields['note'] =  newman.note.GetValue()
      self.db.Insert('mfgs', fields)
      self.UpdateManufacturers()
    
    newman.Destroy()
  
  def OnEdit(self,e):
    #print("edit")
    if self.selected_id == 0:
      return
    where = {}
    where['id'] = self.selected_id
    rows = self.db.Select('mfgs', sqlmfgsfields, where)
    fields = rows[0]
    #print(fields)
    editman = ManufacturerDialog(self, "Edit manufacturer", fields[1], fields[2], fields[3], fields[4], fields[5])
    if editman.ShowModal() == wx.ID_OK:
      fields = {}
      fields['shortname'] =  editman.shortname.GetValue()
      fields['fullname'] =  editman.fullname.GetValue()
      fields['www'] =  editman.www.GetValue()
      fields['address'] =  editman.address.GetValue()
      fields['note'] =  editman.note.GetValue()
      self.db.Update('mfgs', fields, where)
      self.UpdateManufacturers()
    
    editman.Destroy()
    
  def OnDelete(self,e):
    if self.selected_id == 0:
      return
    dlg = wx.MessageDialog(self, "Are you sure to delete this manufacturer? There may be links in spare parts!", "Delete manufacturer", wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      where = {}
      where['id'] = self.selected_id
      self.db.Delete('mfgs', where)
      self.UpdateManufacturers()
    dlg.Destroy()
    
  def OnClose(self, event):
    self.Hide()        
