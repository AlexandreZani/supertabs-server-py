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

from pod.requests import *
from supertabs.auth_db import *
from supertabs.supertabs_db import *
from supertabs.credentials import *

request_factory = RequestFactory()

class LoginRequest(Request):
  REQUEST_TYPE = "Login"
  def __init__(self, args, credentials):
    self.credentials = credentials

  def execute(self, db):
    self.credentials.validateCredentials()
    session = Session(self.credentials.uid)
    self.credentials.db.writeSession(session)

    return { "credentials": {
          "type" : SessionIdCredentials.CREDENTIALS_TYPE,
          "args" : { "sid" : session.sid } } }

request_factory.registerRequestType(LoginRequest)

class GetAllTabsRequest(Request):
  REQUEST_TYPE = "GetAllTabs"
  def __init__(self, args, credentials):
    self.credentials = credentials

  def execute(self, db):
    self.credentials.validateCredentials()
    tabs = db.getAllTabs(self.credentials.uid)

    tabs_table = {}

    for tab in tabs:
      try:
        tabs_table[tab.supertab_id].append(tab)
      except KeyError:
        tabs_table[tab.supertab_id] = [tab]

    result =  { "response" : {
      "supertabs" : [] } }

    for k in tabs_table:
      s = tabs_table[k]
      supertab = { "id" : k, "tabs" : [] }
      for t in s:
        supertab["tabs"].append({ "id" : t.tab_id, "url" : t.url })
      result["response"]["supertabs"].append(supertab)

    return result

request_factory.registerRequestType(GetAllTabsRequest)

class UpdateTabRequest(Request):
  REQUEST_TYPE = "UpdateTab"
  def __init__(self, args, credentials):
    self.credentials = credentials

    try:
      self.tab_id = args["tab_id"]
      self.supertab_id = args["supertab_id"]
      self.url = args["url"]
    except KeyError:
      raise MissingRequestArgument()

  def execute(self, db):
    self.credentials.validateCredentials()

    tab = SupertabTab(self.credentials.uid, self.supertab_id, self.tab_id,
        self.url)

    db.writeTab(tab)

request_factory.registerRequestType(UpdateTabRequest)

class DeleteTabRequest(Request):
  REQUEST_TYPE = "DeleteTab"
  def __init__(self, args, credentials):
    self.credentials = credentials
    try:
      self.supertab_id = args["supertab_id"]
      self.tab_id = args["tab_id"]
    except KeyError:
      raise MissingRequestArgument()

  def execute(self, db):
    self.credentials.validateCredentials()

    db.deleteTab(self.credentials.uid, self.supertab_id, self.tab_id)

request_factory.registerRequestType(DeleteTabRequest)

class PushAllTabsRequest(Request):
  REQUEST_TYPE = "PushAllTabs"
  def __init__(self, args, credentials):
    self.credentials = credentials

    try:
      self.supertabs = args["supertabs"]
    except KeyError:
      raise MissingRequestArgument("supertabs")
  
  def execute(self, db):
    self.credentials.validateCredentials()

    try:
      for s in self.supertabs:
        for t in s["tabs"]:
          db.writeTab(SupertabTab(self.credentials.uid, s["id"], t["id"], t["url"]))
    except KeyError:
      raise MalformedRequest()

request_factory.registerRequestType(PushAllTabsRequest)

