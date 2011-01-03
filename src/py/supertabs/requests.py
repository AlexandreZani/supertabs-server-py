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

from pod.requests import *
from supertabs.auth_db import *
from supertabs.supertabs_db import *
from supertabs.credentials import *

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

RequestFactory.registerRequestType(LoginRequest)
