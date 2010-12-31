#!/usr/bin/python

#   Copyright 2010 Alexandre Zani (alexandre.zani@gmail.com) 
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from supertabs.supertabs_db import *

class MockSupertabsDB(SupertabsDB):
  def __init__(self):
    self.tabs = []

  def writeTab(self, tab):
    self.deleteTab(tab.user_id, tab.supertab_id, tab.tab_id)
    self.tabs.append(tab.clone())

  def deleteTab(self, uid, supertab_id, tab_id):
    for t in self.tabs:
      if t.user_id == uid and t.tab_id == tab_id and t.supertab_id == supertab_id:
        self.tabs.remove(t)
        return True

    return False

  def getTab(self, uid, supertab_id, tab_id):
    for t in self.tabs:
      if t.user_id == uid and t.tab_id == tab_id and t.supertab_id == supertab_id:
        return t.clone()

    return None
  
  def getAllTabs(self, uid):
    ts = []
    for t in self.tabs:
      if t.user_id == uid:
        ts.append(t.clone())

    return ts
