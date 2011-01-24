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
from tests.mock_supertabs_db import *

def pytest_generate_tests(metafunc):
  if 'db' in metafunc.funcargnames:
    metafunc.addcall(param=1)
    metafunc.addcall(param=2)
    metafunc.addcall(param=3)

def pytest_funcarg__db(request):
  if request.param == 1:
    return MockSupertabsDB()
  elif request.param == 2:
    db = create_engine("mysql://test:password@localhost/SupertabsDB")
    metadata = MetaData(db)
    tabs_table = Table('Tabs', metadata, autoload=True)
    tabs_table.delete().execute()
    return SQLAlchemySupertabsDB(db)
  elif request.param == 3:
    db = create_engine('sqlite:///:memory:')
    return SQLAlchemySupertabsDB(db)

class TestDatabase(object):
  def test_writeTab(self, db):
    tab = SupertabTab("uid", 0, 1, "url")
    db.writeTab(tab)
    tab2 = db.getTab("uid", 0, 1)

    assert tab == tab2

  def test_deleteTab(self, db):
    tab = SupertabTab("uid", 0, 1, "url")
    db.writeTab(tab)
    db.deleteTab("uid", 0, 1)
    tab2 = db.getTab("uid", 0, 1)

    assert None == tab2

  def test_rewriteTab(self, db):
    tab = SupertabTab("uid", 0, 1, "url")
    db.writeTab(tab)

    tab.url = "http://www.google.com/"
    db.writeTab(tab)

    tab2 = db.getTab("uid", 0, 1)

    assert tab == tab2
    assert "http://www.google.com/" == tab2.url

  def test_getAllTabs(self, db):
    tab1 = SupertabTab("uid", 10, 11, "url")
    tab2 = SupertabTab("uid", 20, 21, "url2")
    db.writeTab(tab1)
    db.writeTab(tab2)

    tabs = db.getAllTabs("uid")

    assert tab1 in tabs
    assert tab2 in tabs
