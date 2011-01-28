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

from supertabs.auth_db import *

class MockAuthDB(AuthDB):
  def __init__(self):
    self.users = []
    self.sessions = []

  def newUser(self, username, password):
    for user in self.users:
      if user.username == username:
        raise DuplicateUsernameException()

    uid = binascii.hexlify(os.urandom(256/8))
    user = User(uid, username, password)

    self.users.append(user)

    return user.clone()

  def writeUser(self, user):
    self.deleteUser(user.username)
    self.users.append(user.clone())

  def getUser(self, username):
    for user in self.users:
      if user.username == username:
        return user.clone()
    return None

  def deleteUser(self, username):
    for user in self.users:
      if user.username == username:
        self.users.remove(user)
        return True

    return False

  def writeSession(self, session):
    if None != self.getSession(session.sid):
      raise DuplicateSessionIdException()
    self.sessions.append(session)

  def getSession(self, sid):
    for session in self.sessions:
      if session.sid == sid:
        return session.clone()
    return None

  def deleteSession(self, sid):
    for session in self.sessions:
      if session.sid == sid:
        self.sessions.remove(session)
        return True
    return False
