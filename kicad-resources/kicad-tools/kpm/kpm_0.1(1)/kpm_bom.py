#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re
import kpm_db
import kpm_common
import kpm_config

sqlbomfields = [
  'id', 
  'name', 
  'version', 
  'revision',
  'csv'
]

class BOM():
  def __init__(self):
    self.bom = []
    self.bomfields=[]
    
  def ReadBOM(self, filename):
    #print(filename)
    f = open(filename, 'r')
    i = 0
    for line in f:
      line = line.strip('\n')
      line = line.strip('\r')
      fields = line.split(',')
      for j in range(0,len(fields)):
        fields[j] = fields[j].strip()
      if i == 0:
        self.bomfields=fields
      else:
        while len(fields) < len(self.bomfields):
          fields.append('')
        self.bom.append(fields)
      #print(fields)
      i += 1
    f.close()
    
  def ReadPos(self, filename):
    print(filename)
    f = open(filename, 'r')
    num = 0
    names = None
    for line in f:
      line = line.strip('\n')
      line = line.strip('\r')
      if line.startswith('##'):
        continue
      elif line.startswith('# '):
        line = line[2:]
        names = re.split(r'\s{2,}', line)
        #print(names)
        num = len(names)
        ref = names.index('Ref')
        posx = names.index('PosX')
        posy = names.index('PosY')
        rot = names.index('Rot')
        side = names.index('Side')
        reference = self.bomfields.index('Reference')
        self.bomfields.append('PosX');
        self.bomfields.append('PosY');
        self.bomfields.append('Rot');
        self.bomfields.append('Side');
      elif names!=None:
        #split by 2 spaces - why the format is not CSV ? grrrrr
        fields = re.split(r'\s{2,}', line)
        #check number of fields,, if not the same, try to split by one space
        if len(fields) != num:
          fields = re.split(r'\s{1,}', line)
        #if there is space in part value, try to fix it - we don't need it
        while len(fields) > num:
          fields.delete(2)
        #print(fields)
        #find part by reference in bom and update position data
        for b in range(0,len(self.bom)):
          #print(str(b) + ' ' + self.bom[b][reference])
          if self.bom[b][reference] == fields[ref]:
            #print(b)
            #print(fields)
            self.bom[b].append(fields[posx])
            self.bom[b].append(fields[posy])
            self.bom[b].append(fields[rot])
            self.bom[b].append(fields[side])
            #print(self.bom[b])
            break
        #print(self.bom)
    f.close()
    
  def SortBOM(self):
    ref = self.bomfields.index('Value')
    for i in range(0,len(self.bom)):
      for j in range(i+1, len(self.bom)):
        if self.bom[i][ref]>self.bom[j][ref]:
          tmp = self.bom[i]
          self.bom[i] = self.bom[j]
          self.bom[j] = tmp
    
  def BuildCSV(self):
    csv = ""
    i = 0
    for b in self.bomfields:
      if i!=0:
        csv += '\t'
      csv += b
      i += 1
    csv += '\n'
    for f in self.bom:
      i = 0
      for b in f:
        if i!=0:
          csv += '\t'
        csv += b
        i += 1
      csv += '\n'
    return csv
  
  def ParseCSV(self, csv):
    self.bomfields=[]
    self.bom=[]
    lines = csv.split('\n')
    self.bomfields = lines[0].split('\t')
    for i in range(1, len(lines)-1):
      self.bom.append(lines[i].split('\t'))
  
  def WriteCSV(self, filename, csv):
    f = open(filename, 'w')
    f.write(csv)
    f.close()
  

# ---------------------------------------------------------
# BOMImportDialog
# ---------------------------------------------------------

class BOMImportDialog(wx.Dialog):
  def __init__(self, parent, title, name="", version=""):
    wx.Dialog.__init__(self, parent, title=title, size=(355,340))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(8,2)
    self.sizer.Add(self.gridsizer, 1)
   
    self.nametext = wx.StaticText(self, label="Name")
    self.gridsizer.Add(self.nametext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.dummy3 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy3, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.namectrl = wx.TextCtrl(self, -1, size=(300,25))
    self.namectrl.SetValue(name)
    self.gridsizer.Add(self.namectrl, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.dummy4 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy4, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)

    self.versiontext = wx.StaticText(self, label="Version")
    self.gridsizer.Add(self.versiontext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.dummy5 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy5, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.versionctrl = wx.TextCtrl(self, -1, size=(300,25))
    self.versionctrl.SetValue(version)
    self.gridsizer.Add(self.versionctrl, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.dummy6 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy6, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)

    self.bomtext = wx.StaticText(self, label="BOM file")
    self.gridsizer.Add(self.bomtext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.dummy1 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy1, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.bomfilectrl = wx.TextCtrl(self, -1, size=(300,25))
    self.bomfilectrl.SetValue("")
    self.gridsizer.Add(self.bomfilectrl, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.btnBrowseBom = wx.Button(self, 10001, "...", size=(30,25))
    self.gridsizer.Add(self.btnBrowseBom, 0, flag=wx.ALL, border=5)

    self.postext = wx.StaticText(self, label="Position file")
    self.gridsizer.Add(self.postext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.dummy2 = wx.StaticText(self, label="")
    self.gridsizer.Add(self.dummy2, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.posfilectrl = wx.TextCtrl(self, -1, size=(300,25))
    self.posfilectrl.SetValue("")
    self.gridsizer.Add(self.posfilectrl, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.btnBrowsePos = wx.Button(self, 10002, "...", size=(30,25))
    self.gridsizer.Add(self.btnBrowsePos, 0, flag=wx.ALL, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    
    self.Bind(wx.EVT_BUTTON, self.OnBrowseBOM, self.btnBrowseBom)
    self.Bind(wx.EVT_BUTTON, self.OnBrowsePos, self.btnBrowsePos)
    
    self.bomfilename = ""
    self.posfilename = ""
        
  def OnBrowseBOM(self, event):
    filedlg = wx.FileDialog(self, "Open BOM file", os.getcwd(), "", "*.csv", wx.OPEN)
    if filedlg.ShowModal() == wx.ID_OK:
      self.bomfilename = filedlg.GetPath()
      self.bomfilectrl.SetValue(self.bomfilename)
    filedlg.Destroy()
   
  def OnBrowsePos(self, event):
    filedlg = wx.FileDialog(self, "Open positions file", os.getcwd(), "", "*.pos", wx.OPEN)
    if filedlg.ShowModal() == wx.ID_OK:
      self.posfilename = filedlg.GetPath()
      self.posfilectrl.SetValue(self.posfilename)
    filedlg.Destroy()
   
# ---------------------------------------------------------
# BOMDialog
# ---------------------------------------------------------

class BOMDialog(wx.Dialog):
  def __init__(self, parent, title, bomfields, bom):
    wx.Dialog.__init__(self, parent, title=title, size=(800,500), style=wx.RESIZE_BORDER)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    id = wx.NewId()
    self.bom_ctrl = wx.ListCtrl(self, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER, size=(800,500))
    self.sizer.Add(self.bom_ctrl, 1, wx.ALL|wx.EXPAND)
    for i in range(0, len(bomfields)):
      self.bom_ctrl.InsertColumn(i, bomfields[i])
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.bom_ctrl)
    
    self.btnOK = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)
    #self.btnEdit = wx.Button(self, wx.ID_EDIT)
    #self.btnDelete = wx.Button(self, wx.ID_DELETE)

    self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.btnSizer.Add(self.btnOK)
    self.btnSizer.Add(self.btnCancel)
    #self.btnSizer.Add(self.btnDelete)
    #self.btnSizer.Add(self.btnClose)

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()
    
    #self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnClose)
    #self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btnAdd)
    #self.Bind(wx.EVT_BUTTON, self.OnEdit, self.btnEdit)
    #self.Bind(wx.EVT_BUTTON, self.OnDelete, self.btnDelete)
    
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.bomfields = bomfields
    self.bom = bom
    self.UpdateBOM()
    self.selected_id = 0
    
  def UpdateBOM(self):
    i = 0
    self.bom_ctrl.DeleteAllItems()
    for b in self.bom:
      self.bom_ctrl.InsertStringItem(i, str(b[0]))
      for j in range(1,len(b)):
        self.bom_ctrl.SetStringItem(i, j, b[j])
      i+=1

  def OnSelect(self, event):
    item = event.GetItem()
    #self.selected_id = int(item.GetText())
    #print(self.selected_id)
        
  def OnClose(self, event):
    self.Hide()        
    
# ---------------------------------------------------------
# BOM Frame
# ---------------------------------------------------------

class BOMFrame(wx.Dialog):
  def __init__(self, parent, title):
    wx.Dialog.__init__(self, parent, title=title, size=(800,500), style=wx.RESIZE_BORDER)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    id = wx.NewId()
    self.bom_ctrl = wx.ListCtrl(self, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER, size=(800,500))
    self.sizer.Add(self.bom_ctrl, 1, wx.ALL|wx.EXPAND)
    self.bom_ctrl.InsertColumn(0, 'ID', width=30)
    self.bom_ctrl.InsertColumn(1, 'Name', width=80)
    self.bom_ctrl.InsertColumn(2, 'Version', width=150)
    self.bom_ctrl.InsertColumn(3, 'Revision', width=150)
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.bom_ctrl)
    
    self.btnClose = wx.Button(self, wx.ID_CLOSE)
    self.btnImport = wx.Button(self, 10001, "Import")
    self.btnReimport = wx.Button(self, 10002, "Reimport")
    self.btnExport = wx.Button(self, 10002, "Export")
    self.btnView = wx.Button(self, 10003, "View")
    self.btnDelete = wx.Button(self, wx.ID_DELETE)

    self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.btnSizer.Add(self.btnImport)
    self.btnSizer.Add(self.btnReimport)
    self.btnSizer.Add(self.btnExport)
    self.btnSizer.Add(self.btnView)
    self.btnSizer.Add(self.btnDelete)
    self.btnSizer.Add(self.btnClose)

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()
    
    self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnClose)
    self.Bind(wx.EVT_BUTTON, self.OnImport, self.btnImport)
    self.Bind(wx.EVT_BUTTON, self.OnReimport, self.btnReimport)
    self.Bind(wx.EVT_BUTTON, self.OnExport, self.btnExport)
    self.Bind(wx.EVT_BUTTON, self.OnView, self.btnView)
    self.Bind(wx.EVT_BUTTON, self.OnDelete, self.btnDelete)
    
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.UpdateBOMs()
    
    self.selected_id = 0
    self.bom = BOM()
    
  def UpdateBOMs(self):
    boms = self.db.Select('bom', sqlbomfields)
    i = 0
    self.bom_ctrl.DeleteAllItems()
    for bom in boms:
      self.bom_ctrl.InsertStringItem(i, str(bom[0]))
      self.bom_ctrl.SetStringItem(i, 1, bom[1])
      self.bom_ctrl.SetStringItem(i, 2, bom[2])
      self.bom_ctrl.SetStringItem(i, 3, str(bom[3]))
      i+=1
  
  def InsertCSV(self, name, version, csv):
    fields = {}
    fields['name'] = name
    fields['version'] = version
    fields['revision'] = 1
    fields['csv'] = csv
    self.db.Insert('bom', fields)
    #print(csv)
    
  def UpdateCSV(self, id, name, version, revision, csv):
    fields = {}
    fields['name'] = name
    fields['version'] = version
    fields['revision'] = revision
    fields['csv'] = csv
    where = {}
    where['id'] = id
    self.db.Update('bom', fields, where)
    #print(csv)
    
  def AddPartNumbers(self):
    index = self.bom.bomfields.index('Part ID')
    for i in range(0, len(self.bom.bom)):
      partid = self.bom.bom[i][index]
      fields = ['partnumber']
      where = {}
      where['partid'] = partid
      rows = self.db.Select('spares', fields, where)
      pn = ""
      for row in rows:
        if pn != '':
          pn += ","
        pn += row[0]
      self.bom.bom[i].insert(index, pn)
    self.bom.bomfields.insert(index, 'Part Number')
    
  def OnSelect(self, event):
    item = event.GetItem()
    self.selected_id = int(item.GetText())
    print(self.selected_id)
        
  def OnImport(self,e):
    #print("new")
    bomimport = BOMImportDialog(self, "Import BOM")
    if bomimport.ShowModal() == wx.ID_OK:
      self.bom.Clear()
      self.bom.ReadBOM(bomimport.bomfilename)
      self.bom.ReadPos(bomimport.posfilename)
      self.bom.SortBOM()
      #print(csv)
      name = bomimport.namectrl.GetValue()
      version = bomimport.versionctrl.GetValue()
      bomdlg = BOMDialog(self, "Import BOM "+name+" v. "+version+" ?", self.bom.bomfields, self.bom.bom)
      if bomdlg.ShowModal() == wx.ID_OK:
        csv = self.bom.BuildCSV()
        self.bom.InsertCSV(name, version, csv)
        self.UpdateBOMs()
      bomdlg.Destroy()
    
    bomimport.Destroy()
  
  def OnReimport(self,e):
    if self.selected_id == 0:
      return
    where = {}
    where['id'] = self.selected_id
    rows = self.db.Select('bom', sqlbomfields, where)
    fields = rows[0]
    revision = fields[3]
    self.bom.ParseCSV(fields[4])
    bomimport = BOMImportDialog(self, "Reimport BOM", fields[1], fields[2])
    if bomimport.ShowModal() == wx.ID_OK:
      self.bom.Clear()
      self.bom.ReadBOM(bomimport.bomfilename)
      self.bom.ReadPos(bomimport.posfilename)
      self.bom.SortBOM()
      #print(csv)
      name = bomimport.namectrl.GetValue()
      version = bomimport.versionctrl.GetValue()
      bomdlg = BOMDialog(self, "Reimport BOM "+name+" v. "+version+" ?", self.bom.bomfields, self.bom.bom)
      if bomdlg.ShowModal() == wx.ID_OK:
        csv = self.bom.BuildCSV()
        self.UpdateCSV(self.selected_id, name, version, revision+1, csv)
        self.UpdateBOMs()
      bomdlg.Destroy()
    
    bomimport.Destroy()
 
  def OnExport(self,e):
    if self.selected_id == 0:
      return
    where = {}
    where['id'] = self.selected_id
    rows = self.db.Select('bom', sqlbomfields, where)
    fields = rows[0]
    revision = fields[3]
    self.bom.ParseCSV(fields[4])
    self.AddPartNumbers()
    csv = self.bom.BuildCSV()
    filedlg = wx.FileDialog(self, "Export BOM file", os.getcwd(), fields[1]+" v. "+fields[2]+" r. "+str(fields[3])+".csv", "*.csv", wx.SAVE|wx.OVERWRITE_PROMPT)
    if filedlg.ShowModal() == wx.ID_OK:
      bomfilename = filedlg.GetPath()
      self.bom.WriteCSV(bomfilename, csv)
    filedlg.Destroy()
    
  
  def OnView(self,e):
    if self.selected_id == 0:
      return
    where = {}
    where['id'] = self.selected_id
    rows = self.db.Select('bom', sqlbomfields, where)
    fields = rows[0]
    self.bom.ParseCSV(fields[4])
    
    #print(fields)
    bomdlg = BOMDialog(self, "Edit BOM "+fields[1]+" v. "+fields[2], self.bom.bomfields, self.bom.bom)
    bomdlg.ShowModal()
    bomdlg.Destroy()
    
  def OnDelete(self,e):
    if self.selected_id == 0:
      return
    dlg = wx.MessageDialog(self, "Are you sure to delete this BOM?", "Delete BOM", wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      where = {}
      where['id'] = self.selected_id
      self.db.Delete('bom', where)
      self.UpdateBOMs()
    dlg.Destroy()
    
  def OnClose(self, event):
    self.Hide()        
