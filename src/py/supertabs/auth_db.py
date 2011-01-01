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

import hashlib
import os
import binascii
import time

class User(object):
  def __init__(self, uid, username, password, uid_salt = None, password_salt = None):
    if uid_salt == None:
      self.setPassword(password)
      self.setUserId(binascii.unhexlify(uid), password)
      self.username = username
    else:
      self.username = username
      self.password_salt = binascii.unhexlify(password_salt)
      self.uid_salt = binascii.unhexlify(uid_salt)
      self.salted_password = binascii.unhexlify(password)
      self.encrypted_uid = binascii.unhexlify(uid)

  def changePassword(self, old_password, new_password):
    if not self.checkPassword(old_password):
      raise Exception("WrongPassword")
    uid = self.getUserId(old_password)
    self.setPassword(new_password)
    self.setUserId(binascii.unhexlify(uid), new_password)

  def clone(self):
    return User(self.getEncryptedUserId(), self.username,
        self.getSaltedPassword(), self.getUserIdSalt(), self.getPasswordSalt())

  def setPassword(self, new_password):
    self.password_salt = os.urandom(256/8)
    self.salted_password = self.saltPassword(new_password, self.password_salt)

  def saltPassword(self, password, salt):
    sha256 = hashlib.sha256()
    sha256.update(password)
    sha256.update(salt)
    return sha256.hexdigest()

  def checkPassword(self, password):
    test_password = self.saltPassword(password, self.password_salt)
    return test_password == self.salted_password

  def setUserId(self, uid, password):
    self.uid_salt = os.urandom(256/8)
    self.encrypted_uid = self.encryptUserId(uid, password, self.uid_salt)

  def getUserId(self, password):
    return binascii.hexlify(self.encryptUserId(self.encrypted_uid, password, self.uid_salt))

  def getSaltedPassword(self):
    return binascii.hexlify(self.salted_password)

  def getEncryptedUserId(self):
    return binascii.hexlify(self.encrypted_uid)

  def getUserIdSalt(self):
    return binascii.hexlify(self.uid_salt)

  def getPasswordSalt(self):
    return binascii.hexlify(self.password_salt)

  def encryptUserId(self, uid, password, uid_salt):
    sha256 = hashlib.sha256()
    sha256.update(password)
    sha256.update(uid_salt)
    salted_password = sha256.digest()

    result = ""

    for i in range(len(salted_password)):
      result += chr(ord(salted_password[i]) ^ ord(uid[i]))

    return result

  def __eq__(self, right):
    try:
      eq = (self.encrypted_uid == right.encrypted_uid and
          self.salted_password == right.salted_password and
          self.uid_salt == right.uid_salt and
          self.password_salt == right.password_salt and
          self.username == right.username)
    except Exception:
      return False
    return eq

  def __ne__(self, right):
    return not self == right

class Session(object):
  def __init__(self, uid, sid = None, last_touched = None):
    self.uid = uid
    if sid == None:
      self.__sid = os.urandom(256/8)
    else:
      self.sid = sid

    if last_touched == None:
      self.last_touched = time.time()
    else:
      self.last_touched = last_touched

  def clone(self):
    return Session(self.uid, self.sid, self.last_touched)

  def __eq__(self, right):
    try:
      b = (self.uid == right.uid and self.sid == right.sid and
          self.last_touched == right.last_touched)
    except Exception:
      return False

    return b

  def __ne__(self, right):
    return not self == right

  @property
  def last_touched(self):
    return self.__last_session

  @last_touched.setter
  def last_touched(self, val):
    self.__last_session = int(val)

  @property
  def sid(self):
    return binascii.hexlify(self.__sid)

  @sid.setter
  def sid(self, val):
    self.__sid = binascii.unhexlify(val)

  @property
  def uid(self):
    return binascii.hexlify(self.__uid)

  @uid.setter
  def uid(self, val):
    self.__uid = binascii.unhexlify(val)

class AuthDBException(Exception): pass

class DuplicateSessionIdException(AuthDBException): pass

class AuthDB(object):
  def writeUser(self, username): pass
  def getUser(self, username): pass
  def deleteUser(self, username): pass
