#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re
import collections
import shlex
import kpm_config
import kpm_db
import kpm_common

sqlpartfields = [
  'id', 
  'partname', 
  'partlabel', 
  'component', 
  'footprint', 
  'value1',
  'value2',
  'value3',
  'rohs',
  'smd',
  'generic',
  'description',
  'category'
]

sqlpartfieldnames = [
  'ID', 
  'Part name', 
  'Part label', 
  'Component', 
  'Footprint', 
  'Value1',
  'Value2',
  'Value3',
  'RoHS',
  'SMD',
  'Generic',
  'Description',
  'Category'
]

def StrSplit(s):
  return shlex.split(s)

# ---------------------------------------------------------
# Main Frame
# ---------------------------------------------------------

class AnnotateFrame(wx.Dialog):
  def __init__(self, parent, title, filename):
    wx.Dialog.__init__(self, parent, title=title, size=(800,600), style=wx.CAPTION|wx.RESIZE_BORDER)

    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)

    # splitter 1
    self.splitter1 = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
    self.sizer.Add(self.splitter1, 1)
    self.panel1 = wx.Panel(self.splitter1, -1)
    self.panel2 = wx.Panel(self.splitter1, -1)
    #self.panel2.SetBackgroundColour('SEA GREEN')
    self.splitter1.SplitVertically(self.panel1, self.panel2)
    self.splitter1.SetSashGravity(0.33)
    self.splitter1.SetSashPosition(300)
    self.sizer2 = wx.BoxSizer(wx.VERTICAL)
    self.panel2.SetSizer(self.sizer2)

    # splitter 2
    self.splitter2 = wx.SplitterWindow(self.panel2, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
    self.sizer2.Add(self.splitter2, 1, wx.EXPAND | wx.ALL)
    self.panel3 = wx.Panel(self.splitter2, -1)
    #self.panel3.SetBackgroundColour('GREEN')
    self.panel4 = wx.Panel(self.splitter2, -1)
    #self.panel4.SetBackgroundColour('LIME')
    self.splitter2.SplitVertically(self.panel3, self.panel4)
    self.splitter2.SetSashGravity(0.5)
    self.splitter2.SetSashPosition(150)

    #schematic control
    self.sizer1 = wx.BoxSizer(wx.VERTICAL)
    self.panel1.SetSizer(self.sizer1)
    self.schtext = wx.StaticText(self.panel1, label="Schematic")
    self.sizer1.Add(self.schtext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
    id = wx.NewId()
    self.sch_ctrl = wx.ListCtrl(self.panel1, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
    self.sch_ctrl.InsertColumn(0, 'Ref')
    self.sch_ctrl.InsertColumn(1, 'Value')
    self.sch_ctrl.InsertColumn(2, 'Part Name')
    self.sizer1.Add(self.sch_ctrl, 1, wx.ALL|wx.EXPAND)
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSch, self.sch_ctrl)
    #self.maingrid.Add(self.cats_ctrl,0,wx.ALL|wx.EXPAND)

    #parts list
    self.sizer3 = wx.BoxSizer(wx.VERTICAL)
    self.panel3.SetSizer(self.sizer3)
    self.parttext = wx.StaticText(self.panel3, label="Parts")
    self.sizer3.Add(self.parttext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
    id = wx.NewId()
    self.parts_ctrl = kpm_common.AutoWidthListCtrl(self.panel3, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER) #, id, size=(-1,-1), style=wx.LC_REPORT) #|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER
    self.sizer3.Add(self.parts_ctrl, 1, wx.ALL|wx.EXPAND)
    self.parts_ctrl.InsertColumn(0, 'Part name')
    self.find = wx.TextCtrl(self.panel3, -1, size=(300,25))
    self.find.SetValue("")
    self.sizer3.Add(self.find, 0, flag=wx.ALL|wx.EXPAND, border=2)
    
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPart, self.parts_ctrl)
    self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPartActivate, self.parts_ctrl)
    self.Bind(wx.EVT_TEXT, self.OnFind, self.find)

    #properties list
    self.sizer4 = wx.BoxSizer(wx.VERTICAL)
    self.panel4.SetSizer(self.sizer4)
    self.proptext = wx.StaticText(self.panel4, label="Properties")
    self.sizer4.Add(self.proptext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.FIXED_MINSIZE, border=5)
    id = wx.NewId()
    self.prop_ctrl = wx.ListCtrl(self.panel4, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
    self.sizer4.Add(self.prop_ctrl, 2, wx.ALL|wx.EXPAND)
    self.prop_ctrl.InsertColumn(0, 'Property')
    self.prop_ctrl.InsertColumn(1, 'Value')

    # Init database
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.schematic = []

    # Buttons
    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)
    self.Bind(wx.EVT_BUTTON, self.OnOK, self.btnOk)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()
    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)

    # Show window      
    self.Show(True)
    self.LoadSchematic(filename)
    self.UpdateComponents()
    
    # Init variables
    self.selected_part = 0
    self.selected_sch = 0
    self.num_parts = 0

  def LoadSchematic(self, filename):
    #print(filename)
    self.filename = filename
    f = open(filename, 'r')
    self.sch = []
    i = 0
    comp = 0
    for line in f:
      if line.strip() == "$Comp":
        comp = 1
        component = {}
        fields = {}
        other = []
      elif line.strip() == "$EndComp":
        comp = 0
        component['fields'] = fields
        component['other'] = other
        self.sch.append(component)
      elif comp == 1:
        #ws = line.split()
        ws = StrSplit(line)
        #print(ws)
        if ws[0] == 'L':
          component['component'] = ws[1]
          component['refdes'] = ws[2]
        elif ws[0] == 'U':
          component['U'] = line
        elif ws[0] == 'P':
          component['P'] = line
        elif ws[0] == 'F':
          fields[ws[1]] = ws
        else:
          other.append(line)
      else:
        self.sch.append(line)
      #print(line)
      i += 1
    f.close()
    #for h in self.sch:
    #  print(h)
    
  def SaveSchematic(self, filename):
    if os.path.isfile(filename):
      os.rename(filename, filename+".kpmbak")
    f = open(filename, 'w')
    
    for line in self.sch:
      if type(line) is str:
        f.write(line)
      elif type(line) is dict:
        f.write("$Comp\n")
        f.write('L '+line['component'] + ' ' + line['refdes'] + '\n')
        f.write(line['U'])
        f.write(line['P'])
        fields = collections.OrderedDict(sorted(line['fields'].items()))
        #print(fields)
        for l in fields:
          field = fields[str(l)]
          #print(field)
          i = 0
          for s in field:
            if i != 0:
              f.write(" ")
            #print(s)
            if (i == 2) | (i == 10):
              f.write('"'+s+'"')
            else:
              f.write(s)
            i += 1
          f.write("\n")
        for l in line['other']:
          f.write(l)
        f.write("$EndComp\n")
    
    f.close()
    return(1)

  # EVENTS
  def OnSch(self, event):
    item = event.GetItem()
    id = item.GetId()
    self.selected_sch = self.sch_ctrl.GetItemData(id)
    #print(self.selected_sch)
    partlabel = str(self.GetFieldByIndex(self.selected_sch, 1))
    self.find.SetValue(partlabel)
    #self.UpdateParts()
    
  def OnPart(self, event):
    item = event.GetItem()
    id = item.GetId()
    self.selected_part = self.parts_ctrl.GetItemData(id)
    self.UpdatePart(self.selected_part)
    
  def OnFind(self, event):
    self.UpdateParts()
  
  def OnPartActivate(self, event):
    item = event.GetItem()
    id = item.GetId()
    self.selected_part = self.parts_ctrl.GetItemData(id)
    #print(self.selected_part)
    
    where = {}
    where['id'] = self.selected_part
    rows = self.db.Select("parts", sqlpartfields, where)
    prop = rows[0]
    
    item = self.sch_ctrl.GetFirstSelected()
    while (item != -1):
      #print(item)
      sel = self.sch_ctrl.GetItemData(item)
      #print("A" + str(sel))
      self.sch_ctrl.SetStringItem(item, 1, prop[2])  # update part value/label in list
      self.sch_ctrl.SetStringItem(item, 2, prop[1])  # update part name in list
      
      fields = self.sch[sel]['fields']
      fields['1'][2] = prop[2]                       # update part value/label in schematic
      fields['2'][2] = prop[4]                       # update footprint in schematic
      self.SetFieldByName(sel, 'Part Name', prop[1]) # update part name
      self.SetFieldByName(sel, 'Part ID', str(self.selected_part)) # update part id
      
      item = self.sch_ctrl.GetNextSelected(item)
    
#    self.UpdatePart(self.selected_part)
    
  def OnOK(self, event):
    if self.SaveSchematic(self.filename) == 1:
      self.Close()    
    
  # COMMON FUNCTIONS
  def GetFieldByName(self, id, name):
    fields = self.sch[id]['fields']
    for f in fields:
      field = fields[f]
      if len(field) >= 11:
        if field[10] == name:
          return field[2]
    return ""

  def GetFieldByIndex(self, id, index):
    fields = self.sch[id]['fields']
    #print(fields)
    field = fields[str(index)]
    #print(field)
    return field[2]
    
  def SetFieldByName(self, id, name, value):
    fields = self.sch[id]['fields']
    x = 0
    y = 0
    o = 'H'
    nf = 0
    for f in fields:
      field = fields[f]
      if int(field[4])>x:
        x = int(field[4])
      if int(field[5])>y:
        y = int(field[4])
      o = field[3]
      if int(f)>nf:
        nf = int(f)
      if len(field) >= 11:
        if field[10] == name:
          field[2] = value
          return
    nf += 1
    y += 100
    fields[str(nf)] = ['F', str(nf), value, o, str(x), str(y), '60', '0001', 'C', 'CNN', name]

  # UPDATE CONTROLS
  def UpdateComponents(self):
    self.sch_ctrl.DeleteAllItems()
    i = 0
    item = 0
    for comp in self.sch:
      if type(comp) is dict:
        refdes = comp['refdes']
        if refdes[0] != '#':
          self.sch_ctrl.InsertStringItem(item, comp['refdes'])
          fields = comp['fields']
          #print(fields)
          if '1' in fields.keys():
            self.sch_ctrl.SetStringItem(item, 1, fields['1'][2])
          for f in fields:
            field = fields[f]
            #print(field)
            if len(field) >= 11:
              if field[10] == "Part Name":
                self.sch_ctrl.SetStringItem(item, 2, field[2])
          self.sch_ctrl.SetItemData(item, i)
          item += 1
      i += 1
                            
  def UpdateParts(self):
    where = {}
    where['component'] = self.sch[self.selected_sch]['component']
    where['partlabel'] = self.find.GetValue() + '%'
    parts = self.db.Select('parts', ['id', 'partname'], where, 'value1')
    self.prop_ctrl.DeleteAllItems()
    self.parts_ctrl.DeleteAllItems()
    self.selected_part = 0
    i = 0
    for part in parts:
      item = self.parts_ctrl.InsertStringItem(i, part[1])
      self.parts_ctrl.SetItemData(item, long(part[0]))
      i+=1
    self.num_parts = i

  def UpdatePart(self, part):
    where = {}
    where['id'] = part
    rows = self.db.Select("parts", sqlpartfields, where)
    prop = rows[0]
    
    where = {}
    where['id'] = prop[12]
    rows = self.db.Select("categories", ['Value1', 'Value2', 'Value3'], where)
    valnames = rows[0]
    
    self.prop_ctrl.DeleteAllItems()
    for i in range(0, len(prop)-1):
      if i==5:
        fname = valnames[0]
      elif i==6:
        fname = valnames[1]
      elif i==7:
        fname = valnames[2]
      else:
        fname = sqlpartfieldnames[i]
      self.prop_ctrl.InsertStringItem(i, fname)
      if (i >= 5) & (i<=7):
        value = kpm_common.val2elv(prop[i])
      else:
        value = prop[i]
      self.prop_ctrl.SetStringItem(i, 1, unicode(value))

 