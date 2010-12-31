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

from sqlalchemy import *

class SupertabTab(object):
  def __init__(self, uid, supertab_id, tab_id, url):
    self.supertab_id = supertab_id
    self.tab_id = tab_id
    self.url = url
    self.user_id = uid

  def clone(self):
    return SupertabTab(self.user_id, self.supertab_id, self.tab_id, self.url)

  def __eq__(self, right):
    try:
      b = ((self.url == right.url) and (self.user_id == right.user_id) and
          (self.tab_id == right.tab_id) and (self.supertab_id ==
            right.supertab_id))
    except Exception:
      return False
    return b

class SupertabsDB(object):
  def getTab(self, uid, supertab_id, tab_id): pass
  def deleteTab(self, uid, supertab_id, tab_id): pass
  def writeTab(self, tab): pass
  def getAllTabs(self, uid): pass

class SQLAlchemySupertabsDB(SupertabsDB):
  def __init__(self, db):
    self.db_engine = db

  def getConn(self):
    return self.db_engine.connect()

  def writeTab(self, tab):
    self.deleteTab(tab.user_id, tab.supertab_id, tab.tab_id)
    conn = self.getConn()
    metadata = MetaData(conn)

    tabs_table = Table('Tabs', metadata, autoload=True)

    stmt = tabs_table.insert().values(UserId=tab.user_id, TabId=tab.tab_id,
        SupertabId=tab.supertab_id, Url=tab.url)

    result = conn.execute(stmt)

    conn.close()

  def getTab(self, uid, supertab_id, tab_id):
    conn = self.getConn()
    metadata = MetaData(conn)

    tabs_table = Table('Tabs', metadata, autoload=True)

    stmt = tabs_table.select().where(and_(tabs_table.c.UserId==uid,
      tabs_table.c.TabId==tab_id,tabs_table.c.SupertabId==supertab_id))

    result = conn.execute(stmt)

    row = result.fetchone()

    conn.close()

    if not row:
      return None

    return SupertabTab(row.UserId, row.SupertabId, row.TabId, row.Url)

  def deleteTab(self, uid, supertab_id, tab_id):
    conn = self.getConn()
    metadata = MetaData(conn)

    tabs_table = Table('Tabs', metadata, autoload=True)

    stmt = tabs_table.delete().where(and_(tabs_table.c.UserId==uid,
      tabs_table.c.TabId==tab_id,tabs_table.c.SupertabId==supertab_id))

    result = conn.execute(stmt)

    conn.close()

  def getAllTabs(self, uid):
    conn = self.getConn()
    metadata = MetaData(conn)

    tabs_table = Table('Tabs', metadata, autoload=True)

    stmt = tabs_table.select().where(tabs_table.c.UserId==uid)

    result = conn.execute(stmt)

    tabs = []

    for row in result:
      tabs.append(SupertabTab(row.UserId, row.SupertabId, row.TabId, row.Url))

    return tabs

