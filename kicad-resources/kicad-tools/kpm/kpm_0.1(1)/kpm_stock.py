#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re
import kpm_config
import kpm_db
import kpm_common
import kpm_bom

currency = ['USD', 'EUR', 'CZK']

sqlbomfields = [
  'id', 
  'name', 
  'version'
]

sqlstockfields = [
  'id', 
  'count', 
  'price', 
  'currency'
]

sqlflowfields = [
  'f.id',
  'p.partname',
  'f.count',
  'f.price',
  'f.currency',
  'f.description',
  'f.time'
]

# ---------------------------------------------------------
# StockReceiveDialog
# ---------------------------------------------------------

class StockReceiveDialog(wx.Dialog):
  def __init__(self, parent, title):
    wx.Dialog.__init__(self, parent, title=title, size=(300,250))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(6,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.counttext = wx.StaticText(self, label="Count")
    self.gridsizer.Add(self.counttext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.countctrl = wx.TextCtrl(self, -1, size=(300,25))
    self.gridsizer.Add(self.countctrl, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.pricetext = wx.StaticText(self, label="Price")
    self.gridsizer.Add(self.pricetext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.pricesizer = wx.BoxSizer(wx.HORIZONTAL)
    self.gridsizer.Add(self.pricesizer, 0, flag=wx.ALL|wx.EXPAND, border=5)
    
    self.pricectrl = wx.TextCtrl(self, -1, size=(150,25))
    self.pricesizer.Add(self.pricectrl, 1)
    self.currencyctrl = wx.ComboBox(self, -1, size=(100,25), choices=currency)
    self.pricesizer.Add(self.currencyctrl, 1)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,90), style=wx.TE_MULTILINE)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)

# ---------------------------------------------------------
# StockDispatchDialog
# ---------------------------------------------------------

class StockDispatchDialog(wx.Dialog):
  def __init__(self, parent, title):
    wx.Dialog.__init__(self, parent, title=title, size=(250,220))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(2,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.counttext = wx.StaticText(self, label="Count")
    self.gridsizer.Add(self.counttext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.countctrl = wx.TextCtrl(self, -1, size=(300,25))
    self.gridsizer.Add(self.countctrl, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,90), style=wx.TE_MULTILINE)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)

# ---------------------------------------------------------
# BOMDispatchDialog
# ---------------------------------------------------------

class BOMDispatchDialog(wx.Dialog):
  def __init__(self, parent, title):
    wx.Dialog.__init__(self, parent, title=title, size=(350,330))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(3,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.bomtext = wx.StaticText(self, label="BOM")
    self.gridsizer.Add(self.bomtext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.bomctrl = kpm_common.AutoWidthListCtrl(self, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER, size=(300,100))
    self.bomctrl.InsertColumn(0, 'BOM')
    self.gridsizer.Add(self.bomctrl, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.counttext = wx.StaticText(self, label="Count")
    self.gridsizer.Add(self.counttext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.countctrl = wx.TextCtrl(self, -1, size=(300,25))
    self.gridsizer.Add(self.countctrl, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,90), style=wx.TE_MULTILINE)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.UpdateBOMs()
    self.bomid = 0
    
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnBOM, self.bomctrl)
    
  def UpdateBOMs(self):
    boms = self.db.Select('bom', sqlbomfields)
    i = 0
    self.bomctrl.DeleteAllItems()
    for bom in boms:
      self.bomctrl.InsertStringItem(i, bom[1]+' v. '+str(bom[2]))
      self.bomctrl.SetItemData(i, long(bom[0]))
      i+=1
  
  def OnBOM(self, event):
    item = event.GetItem()
    id = item.GetId()
    self.bomid = self.bomctrl.GetItemData(id)
     
# ---------------------------------------------------------
# StockFlow Frame
# ---------------------------------------------------------

class StockFlow(wx.Dialog):
  def __init__(self, parent, title="Stock flow"):
    wx.Dialog.__init__(self, parent, title=title, size=(800,500), style=wx.RESIZE_BORDER)
    self.sizer = wx.FlexGridSizer(3,1)
    #self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.AddGrowableRow(1,10)
    self.sizer.AddGrowableCol(0,1)
    self.SetSizer(self.sizer)
    
    self.datesizer = wx.BoxSizer(wx.HORIZONTAL)
    self.sizer.Add(self.datesizer, 1, wx.ALL)

    self.fromtext = wx.StaticText(self, label="From")
    self.datesizer.Add(self.fromtext, 1, wx.ALL)
    t = wx.DateTime().Today()
    sub = wx.DateSpan().Month()
    t = t - sub
    self.datefrom = wx.DatePickerCtrl(self, -1, size=(100,25), style = wx.DP_DROPDOWN)
    self.datefrom.SetValue(t)
    self.datesizer.Add(self.datefrom, 1, wx.ALL)
    self.totext = wx.StaticText(self, label="      To")
    self.datesizer.Add(self.totext, 1, wx.ALL)
    self.dateto = wx.DatePickerCtrl(self, -1, size=(100,25), style = wx.DP_DROPDOWN)
    self.datesizer.Add(self.dateto, 1, wx.ALL)
    
    id = wx.NewId()
    self.flowctrl = wx.ListCtrl(self, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER, size=(200,100))
    self.sizer.Add(self.flowctrl, 1, wx.ALL|wx.EXPAND)
    self.flowctrl.InsertColumn(0, 'ID', width=50)
    self.flowctrl.InsertColumn(1, 'Date', width=150)
    self.flowctrl.InsertColumn(2, 'Part', width=100)
    self.flowctrl.InsertColumn(3, 'Change', width=100)
    self.flowctrl.InsertColumn(4, 'Price', width=100)
    self.flowctrl.InsertColumn(5, 'Description', width=200)
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.flowctrl)
    
    self.btnClose = wx.Button(self, wx.ID_CLOSE)

    self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.btnSizer.Add(self.btnClose)

    self.sizer.Add(self.btnSizer, 1, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    #self.Fit()
    
    self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnClose)
    
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.UpdateFlow()
    self.selected_id = 0
    
  def UpdateFlow(self):
    datefrom = self.datefrom.GetValue()
    dateto = self.dateto.GetValue()
    df = datefrom.FormatISODate() + ' 0:00:00'
    dt = dateto.FormatISODate() + ' 23:59:59'
    rows = self.db.GetStockFlow(sqlflowfields, where = "(f.time>='"+df+"') AND (f.time<='"+dt+"') ORDER BY f.id DESC")
    i = 0
    self.flowctrl.DeleteAllItems()
    for row in rows:
      self.flowctrl.InsertStringItem(i, str(row[0]))
      self.flowctrl.SetStringItem(i, 1, str(row[6]))
      self.flowctrl.SetStringItem(i, 2, str(row[1]))
      self.flowctrl.SetStringItem(i, 3, str(row[2]))
      self.flowctrl.SetStringItem(i, 4, str(row[3])+' '+str(row[4]))
      self.flowctrl.SetStringItem(i, 5, unicode(row[5]))
      i+=1

  def OnSelect(self, event):
    item = event.GetItem()
    self.selected_id = int(item.GetText())
    #print(self.selected_id)
 
  def OnClose(self, event):
    self.Hide()        
