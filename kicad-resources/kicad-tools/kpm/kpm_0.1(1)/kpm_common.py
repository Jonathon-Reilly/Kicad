#!/usr/bin/env python
import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import re

states = ['Unknown', 'Preliminary', 'In production', 'Not for new designs', 'Obsolete', 'Not working']


def elv2val(text):
  tokenized_input = []
  for token in re.split(r'(\d+(?:\.\d+)?)', text):
    token = token.strip()
    if re.match(r'\d+\.\d+', token):
      tokenized_input.append(float(token))
    elif token.isdigit():
      tokenized_input.append(int(token))
    elif token:
      tokenized_input.append(token)
  value = tokenized_input[0]
  if len(tokenized_input)>1:
    if tokenized_input[1]=='k':
      value *= 1000
    elif tokenized_input[1]=='M':
      value *= 1000000
    elif tokenized_input[1]=='p':
      value *= 1e-12
    elif tokenized_input[1]=='n':
      value *= 1e-9
    elif tokenized_input[1]=='u':
      value *= 1e-6
    elif tokenized_input[1]=='m':
      value *= 1e-3
  return value

def val2elv(value):
  #print(value)
  if value is None:
    return "0"
  value = float(value)
  app=''
  if abs(value)>=1e24:
    value = value/1e24
    app = 'Y'
  elif abs(value)>=1e21:
    value = value/1e21
    app = 'Z'
  elif abs(value)>=1e18:
    value = value/1e18
    app = 'E'
  elif abs(value)>=1e15:
    value = value/1e15
    app = 'P'
  elif abs(value)>=1e12:
    value = value/1e12
    app = 'T'
  elif abs(value)>=1e9:
    value = value/1e9
    app = 'G'
  elif abs(value)>=1e6:
    value = value/1e6
    app = 'M'
  elif abs(value)>=1e3:
    value = value/1e3
    app = 'k'
  elif abs(value)>=1:
    app = ''
  elif abs(value)>=1e-3:
    value = value*1e3
    app = 'm'
  elif abs(value)>=1e-6:
    value = value*1e6
    app = 'u'
  elif abs(value)>=1e-9:
    value = value*1e9
    app = 'n'
  elif abs(value)>=1e-12:
    value = value*1e12
    app = 'p'
  elif abs(value)>=1e-15:
    value = value*1e15
    app = 'f'
  elif abs(value)>=1e-18:
    value = value*1e18
    app = 'a'
  elif abs(value)>=1e-21:
    value = value*1e21
    app = 'z'
  elif abs(value)>=1e-24:
    value = value*1e24
    app = 'y'
  
  value2 = int(value)
  if float(value2)==value:
    value = value2
  res=str(value)+app
  return res
  
class CatID():
  def __init__(self, id, value1name="", value2name="", value3name=""):
    self.id = id
    self.value1name = value1name
    self.value2name = value2name
    self.value3name = value3name
  def ID(self):
    return self.id
      
class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
  def __init__(self, parent, style, size=(100, 100)):
    wx.ListCtrl.__init__(self, parent, -1, style=style, size=size)
    ListCtrlAutoWidthMixin.__init__(self)

class YesNoCtrl(wx.ComboBox):
  def __init__(self, parent, id, size, value):
    choices = ['Yes', 'No']
    wx.ComboBox.__init__(self, parent, id, size=size, style=wx.CB_READONLY, choices=choices)
    if (value==1):
      self.SetValue("Yes")
    else:
      self.SetValue("No")
    
  def GetValue(self):
    v = wx.ComboBox.GetValue(self)
    if v=="Yes":
      return 1;
    else:
      return 0;

class StateCtrl(wx.ComboBox):
  def __init__(self, parent, id, size, value):
    wx.ComboBox.__init__(self, parent, id, size=size, style=wx.CB_READONLY, choices=states)
    self.SetValue(states[value])
    
  def GetValue(self):
    v = wx.ComboBox.GetValue(self)
    res = states.index(v)
    return res
