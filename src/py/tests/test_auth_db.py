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
from tests.mock_auth_db import *
import binascii

class TestUser(object):
  def test_passwordCheck(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    assert user.checkPassword("password")

  def test_passwordCheckFail(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    assert not user.checkPassword("passwsdaord")

  def test_getUserId(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    assert uid == user.getUserId("password")

  def test_initFromEncrypted(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    euid = user.getEncryptedUserId()
    spass = user.getSaltedPassword()
    username = user.username
    uid_salt = user.getUserIdSalt()
    pass_salt = user.getPasswordSalt()

    user2 = User(euid, username, spass, uid_salt, pass_salt)

    user2.checkPassword("password")
    assert user == user2

  def test_inequality(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")
    user2 = User(uid, "username", "password2")

    assert user != user2

  def test_changePassword(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    user.changePassword("password", "new_pass")

    assert user.checkPassword("new_pass")
    assert uid == user.getUserId("new_pass")

class TestSession(object):
  def test_createSession(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"

    session = Session(uid)

    assert uid == session.uid

  def test_createSessionCopy(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)

    assert uid == session.uid
    assert sid == session.sid
    assert last_touched == session.last_touched

  def test_clone(self):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)

    assert session == session.clone()

def pytest_generate_tests(metafunc):
  if 'db' in metafunc.funcargnames:
    metafunc.addcall(param=1)

def pytest_funcarg__db(request):
  if request.param == 1:
    return MockAuthDB()

class TestAuthDB(object):
  def test_writeUser(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)
    
    user2 = db.getUser("username")
    
    assert user == user2

  def test_changeUser(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)
    user.changePassword("password", "new_pass")
    db.writeUser(user)
    
    user2 = db.getUser("username")
    
    assert user == user2

  def test_writeUserNone(self, db):
    user = db.getUser("username")
    
    assert None == user

  def test_deleteUser(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)
    assert db.deleteUser("username")

    user2 = db.getUser("username")

    assert None == user2

  def test_writeSession(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)

    db.writeSession(session)

    session2 = db.getSession(sid)

    assert session == session2

  def test_writeSessionAgain(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)

    db.writeSession(session)

    try:
      db.writeSession(session)
    except DuplicateSessionIdException:
      assert True
    else:
      assert False

  def test_getSessionNone(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)
    db.writeSession(session)

    session2 = db.getSession(uid)
    
    assert None == session2

  def test_deleteSession(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    sid = "9d0153eb9280dcd5dac53a032743e43634c6e38ac7ad96160ca22490aec33e1c"
    last_touched = 12345

    session = Session(uid, sid, last_touched)
    db.writeSession(session)

    db.deleteSession(sid)

    session2 = db.getSession(sid)
    
    assert None == session2
