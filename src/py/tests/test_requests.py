#!/usr/bin/python

#   Copyright 2010-2011 Alexandre Zani (alexandre.zani@gmail.com) 
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

from supertabs.requests import *
from supertabs.credentials import *
from tests.mock_supertabs_db import *
from tests.mock_auth_db import *

class MockCreds(Credentials):
  CREDENTIALS_TYPE = "Mock"
  def __init__(self, args, db):
    self.valid = args["valid"]
    self.uid = args["uid"]
    self.db = db

  def validateCredentials(self):
    if not self.valid:
      raise InvalidCredentials()
    return True

class TestLoginRequest(object):
  def test_normalOp(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    request = request_factory.getRequest("Login", {}, creds)

    response = request.execute(sdb)

    assert 256/8*2 == len(response["credentials"]["args"]["sid"])

class TestGetAllTabsRequest(object):
  def test_normalOp(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    sdb.writeTab(SupertabTab(uid, 0, 0, "url00"))
    sdb.writeTab(SupertabTab(uid, 0, 1, "url01"))
    sdb.writeTab(SupertabTab(uid, 0, 2, "url02"))

    sdb.writeTab(SupertabTab(uid, 1, 0, "url10"))
    sdb.writeTab(SupertabTab(uid, 1, 1, "url11"))
    sdb.writeTab(SupertabTab(uid, 1, 2, "url12"))

    request = request_factory.getRequest("GetAllTabs", {}, creds)
    response = request.execute(sdb)

    test_table = [["" for c in range(3)] for r in range(2)]

    for s in response["response"]["supertabs"]:
      for t in s["tabs"]:
        test_table[s["id"]][t["id"]] = t["url"]
    
    for s in range(2):
      for t in range(3):
        assert "url" + str(s) + str(t) == test_table[s][t]

class TestUpdateTab(object):
  def test_normalOp(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "UpdateTab"
    args = { "supertab_id" : 0, "tab_id" : 1, "url" : "http" }

    request = request_factory.getRequest(method, args, creds)
    response = request.execute(sdb)

    tab = SupertabTab(uid, 0, 1, "http")

    tab2 = sdb.getTab(uid, 0, 1)

    assert tab == tab2

  def test_noSuperTabId(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "UpdateTab"
    args = { "tab_id" : 1, "url" : "http" }

    try:
      request = request_factory.getRequest(method, args, creds)

      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

  def test_noTabId(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "UpdateTab"
    args = { "supertab_id" : 1, "url" : "http" }

    try:
      request = request_factory.getRequest(method, args, creds)

      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

  def test_noUrl(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "UpdateTab"
    args = { "supertab_id" : 0, "tab_id" : 1 }

    try:
      request = request_factory.getRequest(method, args, creds)

      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

class TestDeleteTab(object):
  def test_normalOp(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    tab = SupertabTab(uid, 0, 1, "http")
    sdb.writeTab(tab)

    method = "DeleteTab"
    args = { "supertab_id" : tab.supertab_id, "tab_id" : tab.tab_id }

    request = request_factory.getRequest(method, args, creds)
    response = request.execute(sdb)

    tab2 = sdb.getTab(uid, 0, 1)

    assert None == tab2

  def test_noSupertabId(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    tab = SupertabTab(uid, 0, 1, "http")
    sdb.writeTab(tab)

    method = "DeleteTab"
    args = { "tab_id" : tab.tab_id }

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

  def test_noTabId(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    tab = SupertabTab(uid, 0, 1, "http")
    sdb.writeTab(tab)

    method = "DeleteTab"
    args = { "supertab_id" : tab.supertab_id }

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

  def test_noArgs(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    tab = SupertabTab(uid, 0, 1, "http")
    sdb.writeTab(tab)

    method = "DeleteTab"
    args = {}

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

class TestPushTabs(object):
  def test_normalOp(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "PushAllTabs"
    args = { "supertabs" : [
      { "id" : 0, "tabs" : [
        { "id" : 0, "url" : "urla" },
        { "id" : 1, "url" : "urlb" },
        { "id" : 2, "url" : "urlc" } ]},
      { "id" : 1, "tabs" : [
        { "id" : 0, "url" : "url0" },
        { "id" : 1, "url" : "url1" },
        { "id" : 2, "url" : "url2" } ]} ]}

    request = request_factory.getRequest(method, args, creds)
    response = request.execute(sdb)

    assert "urla" == sdb.getTab(uid, 0, 0).url
    assert "urlb" == sdb.getTab(uid, 0, 1).url
    assert "urlc" == sdb.getTab(uid, 0, 2).url
    assert "url0" == sdb.getTab(uid, 1, 0).url
    assert "url1" == sdb.getTab(uid, 1, 1).url
    assert "url2" == sdb.getTab(uid, 1, 2).url

  def test_noArgs(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "PushAllTabs"
    args = {}

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MissingRequestArgument:
      assert True
    else:
      assert False

  def test_MalformedSupertab(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "PushAllTabs"
    args = { "supertabs" : [
      { "tabs" : [
        { "id" : 0, "url" : "urla" },
        { "id" : 1, "url" : "urlb" },
        { "id" : 2, "url" : "urlc" } ]},
      { "id" : 1, "tabs" : [
        { "id" : 0, "url" : "url0" },
        { "id" : 1, "url" : "url1" },
        { "id" : 2, "url" : "url2" } ]} ]}

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MalformedRequest:
      assert True
    else:
      assert False

  def test_MalformedTab(self):
    sdb = MockSupertabsDB()
    adb = MockAuthDB()

    username = "username"
    password = "password"
    uid = "facd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, username, password)
    adb.writeUser(user)

    cred_args = {"username" : username, "password" : password}
    cred_type = "UsernamePassword"

    creds = credentials_factory.getCredentials(cred_type, cred_args, adb)

    method = "PushAllTabs"
    args = { "supertabs" : [
      { "id" : 0, "tabs" : [
        { "id" : 0, "url" : "urla" },
        { "id" : 1, "url" : "urlb" },
        { "id" : 2, "url" : "urlc" } ]},
      { "id" : 1, "tabs" : [
        { "url" : "url0" },
        { "id" : 1, "url" : "url1" },
        { "id" : 2, "url" : "url2" } ]} ]}

    try:
      request = request_factory.getRequest(method, args, creds)
      response = request.execute(sdb)
    except MalformedRequest:
      assert True
    else:
      assert False
