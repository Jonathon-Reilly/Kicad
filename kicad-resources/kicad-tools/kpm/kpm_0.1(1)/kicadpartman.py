#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re
import kpm_config
import kpm_db
import kpm_common
import kpm_mfgs
import kpm_sup
import kpm_anno
import kpm_bom
import kpm_stock

currency = ['USD', 'EUR', 'CZK']

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
  'state',
  'description'
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
  'State',
  'Description'
]

sqlsparefields = [
  's.id', 
  's.partnumber', 
  'm.shortname', 
  'f.shortname',
  's.state',
  's.description'
]

sqlstockfields = [
  'id', 
  'count', 
  'price', 
  'currency'
]

# ---------------------------------------------------------
# CategoryDialog
# ---------------------------------------------------------

class CategoryDialog(wx.Dialog):
  def __init__(self, parent, title, shortname="", fullname="", value1="", value2="", value3="", description=""):
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

    self.value1text = wx.StaticText(self, label="Value 1 name")
    self.gridsizer.Add(self.value1text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value1 = wx.TextCtrl(self, -1, size=(300,25))
    self.value1.SetValue(value1)
    self.gridsizer.Add(self.value1, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.value2text = wx.StaticText(self, label="Value 2 name")
    self.gridsizer.Add(self.value2text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value2 = wx.TextCtrl(self, -1, size=(300,25))
    self.value2.SetValue(value2)
    self.gridsizer.Add(self.value2, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.value3text = wx.StaticText(self, label="Value 3 name")
    self.gridsizer.Add(self.value3text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value3 = wx.TextCtrl(self, -1, size=(300,25))
    self.value3.SetValue(value3)
    self.gridsizer.Add(self.value3, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,100), style=wx.TE_MULTILINE)
    self.description.SetValue(description)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()
    
# ---------------------------------------------------------
# PartDialog
# ---------------------------------------------------------

class PartDialog(wx.Dialog):
  def __init__(self, parent, title, value1name, value2name, value3name, partname="", partlabel="", component="", footprint="", value1="", value2="", value3="", rohs=0, smd=0, generic=0, state=0, description=""):
    wx.Dialog.__init__(self, parent, title=title, size=(250,200))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(12,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.partnametext = wx.StaticText(self, label="Part name (must be unique)")
    self.gridsizer.Add(self.partnametext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.partname = wx.TextCtrl(self, -1, size=(300,25))
    self.partname.SetValue(partname)
    self.gridsizer.Add(self.partname, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.partlabeltext = wx.StaticText(self, label="Part label (value in KiCAD ~ Part name)")
    self.gridsizer.Add(self.partlabeltext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.partlabel = wx.TextCtrl(self, -1, size=(300,25))
    self.partlabel.SetValue(partlabel)
    self.gridsizer.Add(self.partlabel, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.componenttext = wx.StaticText(self, label="Component (schematic symbol)")
    self.gridsizer.Add(self.componenttext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.component = wx.TextCtrl(self, -1, size=(300,25))
    self.component.SetValue(component)
    self.gridsizer.Add(self.component, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.footprinttext = wx.StaticText(self, label="Footprint")
    self.gridsizer.Add(self.footprinttext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.footprint = wx.TextCtrl(self, -1, size=(300,25))
    self.footprint.SetValue(footprint)
    self.gridsizer.Add(self.footprint, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.value1text = wx.StaticText(self, label=value1name)
    self.gridsizer.Add(self.value1text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value1 = wx.TextCtrl(self, -1, size=(300,25))
    self.value1.SetValue(value1)
    self.gridsizer.Add(self.value1, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.value2text = wx.StaticText(self, label=value2name)
    self.gridsizer.Add(self.value2text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value2 = wx.TextCtrl(self, -1, size=(300,25))
    self.value2.SetValue(value2)
    self.gridsizer.Add(self.value2, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.value3text = wx.StaticText(self, label=value3name)
    self.gridsizer.Add(self.value3text, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.value3 = wx.TextCtrl(self, -1, size=(300,25))
    self.value3.SetValue(value3)
    self.gridsizer.Add(self.value3, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.rohstext = wx.StaticText(self, label="RoHS")
    self.gridsizer.Add(self.rohstext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.rohs = kpm_common.YesNoCtrl(self, -1, size=(100,25), value=rohs)
    self.gridsizer.Add(self.rohs, 0, flag=wx.ALL, border=5)

    self.smdtext = wx.StaticText(self, label="SMD")
    self.gridsizer.Add(self.smdtext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.smd = kpm_common.YesNoCtrl(self, -1, size=(100,25), value=smd)
    self.gridsizer.Add(self.smd, 0, flag=wx.ALL, border=5)

    self.generictext = wx.StaticText(self, label="Generic")
    self.gridsizer.Add(self.generictext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.generic = kpm_common.YesNoCtrl(self, -1, size=(100,25), value=generic)
    self.gridsizer.Add(self.generic, 0, flag=wx.ALL, border=5)

    self.statetext = wx.StaticText(self, label="State")
    self.gridsizer.Add(self.statetext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.state = kpm_common.StateCtrl(self, -1, (300,25), state)
    self.gridsizer.Add(self.state, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,100), style=wx.TE_MULTILINE)
    self.description.SetValue(description)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()    
    
# ---------------------------------------------------------
# SpareDialog
# ---------------------------------------------------------

class SpareDialog(wx.Dialog):
  def __init__(self, parent, title, partnumber="", mfg="", supplier="", state=0, description=""):
    wx.Dialog.__init__(self, parent, title=title, size=(250,200))
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer(self.sizer)
    
    self.gridsizer = wx.FlexGridSizer(5,2)
    self.sizer.Add(self.gridsizer, 1)
    
    self.partnumbertext = wx.StaticText(self, label="Part number")
    self.gridsizer.Add(self.partnumbertext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.partnumber = wx.TextCtrl(self, -1, size=(300,25))
    self.partnumber.SetValue(partnumber)
    self.gridsizer.Add(self.partnumber, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.mfgtext = wx.StaticText(self, label="Manufacturer")
    self.gridsizer.Add(self.mfgtext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.mfg = wx.TextCtrl(self, -1, size=(300,25))
    self.mfg.SetValue(mfg)
    self.gridsizer.Add(self.mfg, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.suppliertext = wx.StaticText(self, label="Supplier")
    self.gridsizer.Add(self.suppliertext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.supplier = wx.TextCtrl(self, -1, size=(300,25))
    self.supplier.SetValue(supplier)
    self.gridsizer.Add(self.supplier, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.statetext = wx.StaticText(self, label="State")
    self.gridsizer.Add(self.statetext, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=3)
    self.state = kpm_common.StateCtrl(self, -1, (300,25), state)
    self.gridsizer.Add(self.state, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.descrtext = wx.StaticText(self, label="Description")
    self.gridsizer.Add(self.descrtext, 0, flag=wx.ALL, border=3)
    self.description = wx.TextCtrl(self, -1, size=(300,100), style=wx.TE_MULTILINE)
    self.description.SetValue(description)
    self.gridsizer.Add(self.description, 0, flag=wx.ALL|wx.EXPAND, border=5)

    self.btnOk = wx.Button(self, wx.ID_OK)
    self.btnCancel = wx.Button(self, wx.ID_CANCEL)

    self.btnSizer = wx.StdDialogButtonSizer()
    self.btnSizer.AddButton(self.btnOk)
    self.btnSizer.AddButton(self.btnCancel)
    self.btnSizer.Realize()

    self.sizer.Add(self.btnSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
    self.Fit()

# ---------------------------------------------------------
# Main Frame
# ---------------------------------------------------------

class MainFrame(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(800,600))
    self.CreateStatusBar() # A StatusBar in the bottom of the window

    # splitter 1
    self.splitter1 = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
    self.panel1 = wx.Panel(self.splitter1, -1)
    self.panel2 = wx.Panel(self.splitter1, -1)
    #self.panel2.SetBackgroundColour('SEA GREEN')
    self.splitter1.SplitVertically(self.panel1, self.panel2)
    self.splitter1.SetSashGravity(0.33)
    self.splitter1.SetSashPosition(200)
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
    self.splitter2.SetSashPosition(200)

    #categories control
    self.sizer1 = wx.BoxSizer(wx.VERTICAL)
    self.panel1.SetSizer(self.sizer1)
    self.cattext = wx.StaticText(self.panel1, label="Categories")
    self.sizer1.Add(self.cattext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
    self.cats_ctrl = wx.TreeCtrl(self.panel1)
    self.sizer1.Add(self.cats_ctrl, 1, wx.ALL|wx.EXPAND)
    #self.maingrid.Add(self.cats_ctrl,0,wx.ALL|wx.EXPAND)
    self.rootcat = self.cats_ctrl.AddRoot("Categories")
    self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnCategory, self.cats_ctrl)

    #parts list
    self.sizer3 = wx.BoxSizer(wx.VERTICAL)
    self.panel3.SetSizer(self.sizer3)
    self.parttext = wx.StaticText(self.panel3, label="Parts")
    self.sizer3.Add(self.parttext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
    id = wx.NewId()
    self.parts_ctrl = kpm_common.AutoWidthListCtrl(self.panel3, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER) #, id, size=(-1,-1), style=wx.LC_REPORT) #|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER
    self.sizer3.Add(self.parts_ctrl, 1, wx.ALL|wx.EXPAND)
    self.parts_ctrl.InsertColumn(0, 'Part name')
    #self.parts_ctrl.InsertStringItem(0, 'Part 165464643643643')
    #self.parts_ctrl.InsertStringItem(1, 'Part 2')
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPart, self.parts_ctrl)

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
    #self.prop_ctrl.InsertStringItem(0, 'ID')
    #self.prop_ctrl.SetStringItem(0, 1, '123456')
    #self.prop_ctrl.InsertStringItem(0, 'Part name')
    #self.prop_ctrl.SetStringItem(0, 1, 'JHVJH36546345')

    #spares list
    self.sparetext = wx.StaticText(self.panel4, label="Spares")
    self.sizer4.Add(self.sparetext, 0, flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.FIXED_MINSIZE, border=5)
    id = wx.NewId()
    self.spare_ctrl = wx.ListCtrl(self.panel4, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
    self.sizer4.Add(self.spare_ctrl, 1, wx.ALL|wx.EXPAND)
    self.spare_ctrl.InsertColumn(0, 'ID')
    self.spare_ctrl.InsertColumn(1, 'Part number')
    self.spare_ctrl.InsertColumn(2, 'Manufacturer')
    self.spare_ctrl.InsertColumn(3, 'Supplier')
    self.spare_ctrl.InsertColumn(4, 'State')
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSpare, self.spare_ctrl)
    #self.spare_ctrl.InsertStringItem(0, '46465')
    #self.spare_ctrl.SetStringItem(0, 1, 'HJV545-HGJH')
    #self.spare_ctrl.SetStringItem(0, 2, 'Microchip')
    #self.spare_ctrl.InsertStringItem(3, 'TME')
    #self.spare_ctrl.SetStringItem(0, 1, 'JHVJH36546345')

    #self.cats_ctrl.FitInside()
    #self.GetSizer().SetSizeHints(self)
    #self.Fit()

    # Setting up the main menu
    filemenu= wx.Menu()
    partmanmenu = wx.Menu()
    listsmenu = wx.Menu()
    kicadmenu = wx.Menu()
    helpmenu = wx.Menu()

    # File and Help menu
    # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
    self.menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
    self.menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About","About KiCAD Part Manager")

    # Part manager menu
    self.menuAddCategory = partmanmenu.Append(101, "Add &category","Add new subcategory to selected category")
    self.menuAddPart = partmanmenu.Append(102, "Add &part","Add new part to selected category")
    self.menuAddSpare = partmanmenu.Append(103, "Add &spare","Add new spare part to selected part")
    partmanmenu.AppendSeparator()
    self.menuEditCategory = partmanmenu.Append(104, "Edit ca&tegory","Edit selected category")
    self.menuEditPart = partmanmenu.Append(105, "Edit par&t","Edit selected part")
    self.menuEditSpare = partmanmenu.Append(106, "Edit spa&re","Edit selected spare part")
    partmanmenu.AppendSeparator()
    self.menuDeleteCategory = partmanmenu.Append(107, "Delete category","Delete selected category")
    self.menuDeletePart = partmanmenu.Append(108, "Delete part","Delete selected part")
    self.menuDeleteSpare = partmanmenu.Append(109, "Delete spare","Delete selected spare part")

    # Lists menu
    self.menuReceivePart = listsmenu.Append(201, "&Receive part","Receive part to inventory")
    #self.menuReceiveBOM = listsmenu.Append(202, "R&eceive BOM","Receive BOM to inventory")
    self.menuDispatchPart = listsmenu.Append(203, "&Dispatch part","Dispatch part from inventory")
    self.menuDispatchBOM = listsmenu.Append(204, "D&ispatch BOM","Dispatch BOM from inventory")
    self.menuStockFlow = listsmenu.Append(205, "Stock &flow","View stock flow")
    listsmenu.AppendSeparator()
    self.menuManufacturers = listsmenu.Append(206, "&Manufacturers","List, add, edit and delete manufacturers")
    self.menuSuppliers = listsmenu.Append(207, "&Suppliers","List, add, edit and delete suppliers")
    self.menuBOMs = listsmenu.Append(208, "&BOMs","Bill of materials")

    # KiCAD menu
    self.menuAssignParts = kicadmenu.Append(301, "&Assign parts to schematic","Select schematic and assign parts to components")
    #kicadmenu.AppendSeparator()
    #self.menuImportBOM = kicadmenu.Append(302, "&Import BOM","Import BOM")

    # Create the menubar
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File")
    menuBar.Append(partmanmenu,"&Parts")
    menuBar.Append(listsmenu,"&Stock")
    menuBar.Append(kicadmenu,"&KiCAD")
    menuBar.Append(helpmenu,"&Help")
    self.SetMenuBar(menuBar)

    # Set events
    self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
    self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
    self.Bind(wx.EVT_MENU, self.OnAddCategory, self.menuAddCategory)
    self.Bind(wx.EVT_MENU, self.OnEditCategory, self.menuEditCategory)
    self.Bind(wx.EVT_MENU, self.OnAddPart, self.menuAddPart)
    self.Bind(wx.EVT_MENU, self.OnEditPart, self.menuEditPart)
    self.Bind(wx.EVT_MENU, self.OnAddSpare, self.menuAddSpare)
    self.Bind(wx.EVT_MENU, self.OnEditSpare, self.menuEditSpare)
    self.Bind(wx.EVT_MENU, self.OnDeleteCategory, self.menuDeleteCategory)
    self.Bind(wx.EVT_MENU, self.OnDeletePart, self.menuDeletePart)
    self.Bind(wx.EVT_MENU, self.OnDeleteSpare, self.menuDeleteSpare)
    self.Bind(wx.EVT_MENU, self.OnReceivePart, self.menuReceivePart)
    #self.Bind(wx.EVT_MENU, self.OnReceiveBOM, self.menuReceiveBOM)
    self.Bind(wx.EVT_MENU, self.OnDispatchPart, self.menuDispatchPart)
    self.Bind(wx.EVT_MENU, self.OnDispatchBOM, self.menuDispatchBOM)
    self.Bind(wx.EVT_MENU, self.OnStockFlow, self.menuStockFlow)
    self.Bind(wx.EVT_MENU, self.OnManufacturers, self.menuManufacturers)
    self.Bind(wx.EVT_MENU, self.OnSuppliers, self.menuSuppliers)
    self.Bind(wx.EVT_MENU, self.OnBOMs, self.menuBOMs)
    self.Bind(wx.EVT_MENU, self.OnAssignParts, self.menuAssignParts)
    #self.Bind(wx.EVT_MENU, self.OnImportBOM, self.menuImportBOM)

    # Init database
    self.db = kpm_db.Kpm_Db(kpm_config.sqlconfig)
    self.categories = []

    # Show window      
    self.Show(True)
    self.UpdateCategories()
    
    # Init variables
    self.selected_cat = 0
    self.selected_part = 0
    self.selected_spare = 0
    self.num_parts = 0
    
    # Init dialogs
    self.mfgdlg = None
    self.supdlg = None
    self.bomdlg = None

  def OnAbout(self,e):
    # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
    dlg = wx.MessageDialog( self, "KiCAD Part Manager\n\nProgrammed by Mike Crash\n\nLicensed by GNU GPL v3", "About", wx.OK|wx.ICON_INFORMATION)
    dlg.ShowModal() # Show it
    dlg.Destroy() # finally destroy it when finished.

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

  def OnAddCategory(self,e):
    print("new")
    newcat = CategoryDialog(self, "New category")
    if newcat.ShowModal() == wx.ID_OK:
      print(newcat.shortname.GetValue())
      fields = {}
      fields['parent'] =  self.selected_cat
      fields['shortname'] =  newcat.shortname.GetValue()
      fields['fullname'] =  newcat.fullname.GetValue()
      fields['value1'] =  newcat.value1.GetValue()
      fields['value2'] =  newcat.value2.GetValue()
      fields['value3'] =  newcat.value3.GetValue()
      fields['description'] =  newcat.description.GetValue()
      self.db.Insert('categories', fields)
      self.UpdateCategories()
    
    newcat.Destroy()
  
  def OnEditCategory(self,e):
    print("edit")
    if self.selected_cat == 0:
      return
    fields = self.db.GetCategory(self.selected_cat)
    print(fields)
    editcat = CategoryDialog(self, "Edit category", fields[1], fields[2], fields[3], fields[4], fields[5], fields[6])
    if editcat.ShowModal() == wx.ID_OK:
      fields = {}
      fields['shortname'] =  editcat.shortname.GetValue()
      fields['fullname'] =  editcat.fullname.GetValue()
      fields['value1'] =  editcat.value1.GetValue()
      fields['value2'] =  editcat.value2.GetValue()
      fields['value3'] =  editcat.value3.GetValue()
      fields['description'] =  editcat.description.GetValue()
      where = {}
      where['id'] = self.selected_cat
      self.db.Update('categories', fields, where)
      self.UpdateCategories()
    
    editcat.Destroy()

  def OnAddPart(self,e):
    partdlg = PartDialog(self, "New part", self.value1name, self.value2name, self.value3name)
    if partdlg.ShowModal() == wx.ID_OK:
      fields = {}
      fields['category'] =  self.selected_cat
      fields['partname'] =  partdlg.partname.GetValue()
      fields['partlabel'] =  partdlg.partlabel.GetValue()
      fields['component'] =  partdlg.component.GetValue()
      fields['footprint'] =  partdlg.footprint.GetValue()
      fields['value1'] =  kpm_common.elv2val(partdlg.value1.GetValue())
      fields['value2'] =  kpm_common.elv2val(partdlg.value2.GetValue())
      fields['value3'] =  kpm_common.elv2val(partdlg.value3.GetValue())
      fields['rohs'] =  partdlg.rohs.GetValue()
      fields['smd'] =  partdlg.smd.GetValue()
      fields['generic'] =  partdlg.generic.GetValue()
      fields['state'] = partdlg.state.GetValue()
      fields['description'] =  partdlg.description.GetValue()
      self.db.Insert('parts', fields)
      self.UpdateParts(self.selected_cat)
    
    partdlg.Destroy()

  def OnEditPart(self,e):
    if self.selected_part == 0:
      return
    where = {}
    where['id'] = self.selected_part
    rows = self.db.Select('parts', sqlpartfields, where)
    fields = rows[0]
    partdlg = PartDialog(self, "Edit part", self.value1name, self.value2name, self.value3name, fields[1], fields[2], fields[3], fields[4], kpm_common.val2elv(fields[5]), kpm_common.val2elv(fields[6]), kpm_common.val2elv(fields[7]), fields[8], fields[9], fields[10], fields[11], fields[12])
    if partdlg.ShowModal() == wx.ID_OK:
      fields = {}
      fields['category'] =  self.selected_cat
      fields['partname'] =  partdlg.partname.GetValue()
      fields['partlabel'] =  partdlg.partlabel.GetValue()
      fields['component'] =  partdlg.component.GetValue()
      fields['footprint'] =  partdlg.footprint.GetValue()
      fields['value1'] =  kpm_common.elv2val(partdlg.value1.GetValue())
      fields['value2'] =  kpm_common.elv2val(partdlg.value2.GetValue())
      fields['value3'] =  kpm_common.elv2val(partdlg.value3.GetValue())
      fields['rohs'] =  partdlg.rohs.GetValue()
      fields['smd'] =  partdlg.smd.GetValue()
      fields['generic'] =  partdlg.generic.GetValue()
      fields['state'] =  partdlg.state.GetValue()
      fields['description'] =  partdlg.description.GetValue()
      where = {}
      where['id'] = self.selected_part
      self.db.Update('parts', fields, where)
      self.UpdatePart(self.selected_part)
    
    partdlg.Destroy()
    
  def OnAddSpare(self,e):
    sparedlg = SpareDialog(self, "New spare")
    if sparedlg.ShowModal() == wx.ID_OK:
      fields = {}
      fields['partid'] = self.selected_part
      fields['partnumber'] = sparedlg.partnumber.GetValue()
      fields['mfg'] =  self.db.GetManufacturer(sparedlg.mfg.GetValue())
      fields['supplier'] =  self.db.GetSupplier(sparedlg.supplier.GetValue())
      fields['state'] = sparedlg.state.GetValue()
      fields['description'] = sparedlg.description.GetValue()
      self.db.Insert('spares', fields)
      self.UpdateSpares(self.selected_part)
    
    sparedlg.Destroy()

  def OnEditSpare(self,e):
    if self.selected_spare == 0:
      return
    fields = self.db.GetSpare(self.selected_spare, sqlsparefields)
    sparedlg = SpareDialog(self, "Edit spare", fields[1], fields[2], fields[3], fields[4], fields[5])
    if sparedlg.ShowModal() == wx.ID_OK:
      fields = {}
      fields['partnumber'] =  sparedlg.partnumber.GetValue()
      fields['mfg'] =  self.db.GetManufacturer(sparedlg.mfg.GetValue())
      fields['supplier'] =  self.db.GetSupplier(sparedlg.supplier.GetValue())
      fields['state'] = sparedlg.state.GetValue()
      fields['description'] = sparedlg.description.GetValue()
      where = {}
      where['id'] = self.selected_spare
      self.db.Update('spares', fields, where)
      self.UpdateSpares(self.selected_part)
    
    sparedlg.Destroy()

  def OnDeleteCategory(self,e):
    if self.selected_cat == 0:
      return
    if self.num_parts != 0:
      dlg = wx.MessageDialog(self, "Category must be empty to delete it.", "Warning", wx.OK|wx.ICON_INFORMATION)
      dlg.ShowModal()
      return
    dlg = wx.MessageDialog(self, "Are you sure to delete this category?", "Delete category", wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      where = {}
      where['id'] = self.selected_cat
      self.db.Delete('categories', where)
      self.UpdateCategories()
    dlg.Destroy()

  def OnDeletePart(self,e):
    if self.selected_part == 0:
      return
    dlg = wx.MessageDialog(self, "Are you sure to delete this part and all assigned spares?", "Delete part", wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      where = {}
      where['id'] = self.selected_part
      self.db.Delete('parts', where)
      where = {}
      where['partid'] = self.selected_part
      self.db.Delete('spares', where)
      self.UpdateParts(self.selected_cat)
    dlg.Destroy()

  def OnDeleteSpare(self,e):
    if self.selected_spare == 0:
      return
    dlg = wx.MessageDialog(self, "Are you sure to delete this spare?", "Delete spare", wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
      where = {}
      where['id'] = self.selected_spare
      self.db.Delete('spares', where)
      self.UpdateSpares(self.selected_part)
    dlg.Destroy()

  def OnReceivePart(self, e):
    if self.selected_part == 0:
      return
    dlg = kpm_stock.StockReceiveDialog(self, "Receive part to inventory")
    if dlg.ShowModal() == wx.ID_OK:
      count = int(dlg.countctrl.GetValue())
      price = float(dlg.pricectrl.GetValue())
      currency = dlg.currencyctrl.GetValue()
      description = dlg.description.GetValue()
      self.db.Stock(self.selected_part, count, price, currency, description=description)
      self.UpdatePart(self.selected_part)
      
    dlg.Destroy()
    
  def OnReceiveBOM(self, e):
    print("Not implemented")
    
  def OnDispatchPart(self, e):
    if self.selected_part == 0:
      return
    dlg = kpm_stock.StockDispatchDialog(self, "Dispatch part from inventory")
    if dlg.ShowModal() == wx.ID_OK:
      count = -int(dlg.countctrl.GetValue())
      description = dlg.description.GetValue()
      self.db.Stock(self.selected_part, count, description=description)
      self.UpdatePart(self.selected_part)
      
    dlg.Destroy()
    
  def OnDispatchBOM(self, e):
    dlg = kpm_stock.BOMDispatchDialog(self, "Dispatch BOM from inventory")
    if dlg.ShowModal() == wx.ID_OK:
      bomid = dlg.bomid
      count = -int(dlg.countctrl.GetValue())
      description = dlg.description.GetValue()
      where = {}
      where['id'] = bomid
      rows = self.db.Select('bom', kpm_bom.sqlbomfields, where)
      fields = rows[0]
      bom = kpm_bom.BOM()
      bom.ParseCSV(fields[4])
      partid = bom.bomfields.index('Part ID')
      try:
        bomtypeid = bom.bomfields.index('BOMType')
      except:
        bomtypeid = -1
      for part in bom.bom:
        try:
          id = int(part[partid])
        except:
          id = 0
        if bomtypeid>0:
          bomtype = part[bomtypeid]
        else:
          bomtype = ''
        if (id>0) & (bomtype==''):   # TODO make use of variants as NABC = NOT A,B,C
          self.db.Stock(id, count, bom=bomid, description=description)
      self.UpdatePart(self.selected_part)
    
  def OnStockFlow(self, e):
    dlg = kpm_stock.StockFlow(self)
    dlg.ShowModal()
    dlg.Destroy()
    
  def OnManufacturers(self,e):
    if self.mfgdlg is None:
      self.mfgdlg = kpm_mfgs.ManufacturersFrame(self, "Manufacturers")
    self.mfgdlg.Show()
    #mfgdlg.Destroy()

  def OnSuppliers(self,e):
    if self.supdlg is None:
      self.supdlg = kpm_sup.SuppliersFrame(self, "Suppliers")
    self.supdlg.Show()
    #supdlg.Destroy()

  def OnBOMs(self,e):
    if self.bomdlg is None:
      self.bomdlg = kpm_bom.BOMFrame(self, "Bill of material")
    self.bomdlg.Show()
    #bomdlg.Destroy()

  def OnAssignParts(self,e):
    filedlg = wx.FileDialog(self, "Open schematic file", os.getcwd(), "", "*.sch", wx.OPEN)
    if filedlg.ShowModal() == wx.ID_OK:
      filename = filedlg.GetPath()
      #filename = os.path.basename(path)
      dlg = kpm_anno.AnnotateFrame(self, "Assign parts to schematic", filename)
      dlg.ShowModal()
      dlg.Destroy()
    filedlg.Destroy()

  def OnImportBOM(self,e):
    print("OnImportBOM")

  def UpdateCategories(self):
    #print("UpdateCategories")
    cats = self.db.GetCategories(-1)
    self.cats_ctrl.DeleteAllItems()
    self.categories_count = 0
    self.categories = []
    self.rootcat = self.cats_ctrl.AddRoot("Categories")
    sel = kpm_common.CatID(0)
    self.cats_ctrl.SetItemData(self.rootcat, wx.TreeItemData(sel))
    for t in cats:
      if t[1] == 0:
        item = self.cats_ctrl.AppendItem(self.rootcat, t[2])
      else:
        for cat in self.categories:
          if cat[0] == t[1]:
            item = self.cats_ctrl.AppendItem(cat[2], t[2])
            break
      sel = kpm_common.CatID(t[0], t[3], t[4], t[5])
      #TODO check item if exists
      if item != None:
        self.cats_ctrl.SetItemData(item, wx.TreeItemData(sel))
        self.categories.append([t[0], t[1], item])

    #item = self.cats_ctrl.AppendItem(self.rootcat, "Item1")
    #sel = CatID(1)
    #self.cats_ctrl.SetItemData(item, wx.TreeItemData(sel))
    self.cats_ctrl.ExpandAll()

  def UpdateParts(self,category):
    #parts = [] 
    parts = self.db.GetParts(category)
    self.prop_ctrl.DeleteAllItems()
    self.parts_ctrl.DeleteAllItems()
    self.spare_ctrl.DeleteAllItems()
    self.selected_part = 0
    self.selected_spare = 0
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
    self.prop_ctrl.DeleteAllItems()
    i = 0
    for p in prop:
      if i==5:
        fname = self.value1name
      elif i==6:
        fname = self.value2name
      elif i==7:
        fname = self.value3name
      else:
        fname = sqlpartfieldnames[i]
      self.prop_ctrl.InsertStringItem(i, fname)
      if (i >= 5) & (i<=7):
        value = kpm_common.val2elv(p)
      elif (i == 11):
        value = kpm_common.states[p]
      else:
        value = p
      self.prop_ctrl.SetStringItem(i, 1, unicode(value))
      i+=1
    
    rows = self.db.Select("stock", sqlstockfields, where)
    if len(rows)>0:
      prop = rows[0]
      self.prop_ctrl.InsertStringItem(i, 'In stock')
      self.prop_ctrl.SetStringItem(i, 1, unicode(prop[1]))
      i += 1
      if prop[2]!= 0:
        self.prop_ctrl.InsertStringItem(i, 'Price')
        self.prop_ctrl.SetStringItem(i, 1, unicode(prop[2])+' '+unicode(prop[3]))

  def UpdateSpares(self, part):
    spares = self.db.GetSpares(part, sqlsparefields)
    #print(spares)
    self.spare_ctrl.DeleteAllItems()
    i = 0
    for spare in spares:
      self.spare_ctrl.InsertStringItem(i, str(spare[0]))
      self.spare_ctrl.SetStringItem(i, 1, spare[1])
      self.spare_ctrl.SetStringItem(i, 2, spare[2])
      self.spare_ctrl.SetStringItem(i, 3, spare[3])
      self.spare_ctrl.SetStringItem(i, 4, kpm_common.states[spare[4]])
      i+=1

  def OnCategory(self, event):
    item = event.GetItem()
    if item == None:
      return
    itemdata = self.cats_ctrl.GetItemData(item)
    if itemdata == None:
      return
    sel = itemdata.GetData()
    self.selected_cat = sel.ID()
    self.value1name = sel.value1name
    self.value2name = sel.value2name
    self.value3name = sel.value3name
    #print(self.selected_cat)
    self.UpdateParts(self.selected_cat)

  def OnPart(self, event):
    item = event.GetItem()
    id = item.GetId()
    self.selected_part = self.parts_ctrl.GetItemData(id)
    self.selected_spare = 0
    #print(self.selected_part)
    self.UpdatePart(self.selected_part)
    self.UpdateSpares(self.selected_part)
        
  def OnSpare(self, event):
    item = event.GetItem()
    #print(item.GetText())
    self.selected_spare = int(item.GetText())
    #print(self.selected_spare)
        

app = wx.App(False)
frame = MainFrame(None, "KiCAD Part Manager")
app.MainLoop()