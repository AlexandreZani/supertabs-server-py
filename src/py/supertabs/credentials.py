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

from pod.credentials import *
import time

credentials_factory = CredentialsFactory()

class UsernamePasswordCredentials(Credentials):
  CREDENTIALS_TYPE = "UsernamePassword"
  def __init__(self, args, db):
    try:
      self.db = db
      self.username = args["username"]
      self.password = args["password"]

      self.user = db.getUser(self.username)

      if self.user == None:
        raise InvalidCredentials()

      self.uid = self.user.getUserId("password")
    except (KeyError,InvalidCredentials,):
      self.invalid = True
      return
    else:
      self.invalid = False

  def validateCredentials(self):
    if self.invalid or not self.user.checkPassword(self.password):
      raise InvalidCredentials()

    return True

credentials_factory.registerCredentialsType(UsernamePasswordCredentials)

class SessionIdCredentials(Credentials):
  CREDENTIALS_TYPE = "SessionId"

  def __init__(self, args, db):
    try:
      self.db = db
      self.sid = args["sid"]

      self.session = db.getSession(self.sid)
      self.uid = self.session.uid
    except Exception:
      self.invalid = True
    else:
      self.invalid = False

  def validateCredentials(self):
    if self.invalid or time.time() - self.session.last_touched > 60*60*24:
      raise InvalidCredentials()
    self.session.touch()
    self.db.deleteSession(self.session.sid)
    self.db.writeSession(self.session)
    return True

credentials_factory.registerCredentialsType(SessionIdCredentials)

