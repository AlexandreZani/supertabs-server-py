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
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

class User(object):
  def __init__(self, uid, username, password, uid_salt = None, password_salt = None):
    if uid_salt == None:
      self.setPassword(password)
      self.setUserId(binascii.unhexlify(uid), password)
      self.username = username
    else:
      self.username = username
      self.password_salt = password_salt
      self.uid_salt = uid_salt
      self.salted_password = password
      self.encrypted_uid = uid

  @property
  def password_salt(self):
    return binascii.hexlify(self.__password_salt)

  @password_salt.setter
  def password_salt(self, val):
    self.__password_salt = binascii.unhexlify(val)

  @property
  def uid_salt(self):
    return binascii.hexlify(self.__uid_salt)

  @uid_salt.setter
  def uid_salt(self, val):
    self.__uid_salt = binascii.unhexlify(val)

  @property
  def encrypted_uid(self):
    return binascii.hexlify(self.__encrypted_uid)

  @encrypted_uid.setter
  def encrypted_uid(self, val):
    self.__encrypted_uid = binascii.unhexlify(val)

  @property
  def salted_password(self):
    return binascii.hexlify(self.__salted_password)

  @salted_password.setter
  def salted_password(self, val):
    self.__salted_password = binascii.unhexlify(val)

  def changePassword(self, old_password, new_password):
    if not self.checkPassword(old_password):
      raise Exception("WrongPassword")
    uid = self.getUserId(old_password)
    self.setPassword(new_password)
    self.setUserId(binascii.unhexlify(uid), new_password)

  def clone(self):
    return User(self.encrypted_uid, self.username,
        self.salted_password, self.uid_salt, self.password_salt)

  def setPassword(self, new_password):
    self.__password_salt = os.urandom(256/8)
    self.__salted_password = self.saltPassword(new_password, self.__password_salt)

  def saltPassword(self, password, salt):
    sha256 = hashlib.sha256()
    sha256.update(password)
    sha256.update(salt)
    return sha256.hexdigest()

  def checkPassword(self, password):
    test_password = self.saltPassword(password, self.__password_salt)
    return test_password == self.__salted_password

  def setUserId(self, uid, password):
    self.__uid_salt = os.urandom(256/8)
    self.__encrypted_uid = self.encryptUserId(uid, password, self.__uid_salt)

  def getUserId(self, password):
    return binascii.hexlify(self.encryptUserId(self.__encrypted_uid, password,
      self.__uid_salt))

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

  def touch(self):
    self.last_touched = time.time()

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

class DuplicateUsernameException(AuthDBException): pass

class AuthDB(object):
  def writeUser(self, username): pass
  def getUser(self, username): pass
  def deleteUser(self, username): pass
  def writeSession(self, session): pass
  def getSession(self, sid): pass
  def deleteSession(self, sid): pass

class SQLAlchemyAuthDB(AuthDB):
  def __init__(self, db):
    self.db_engine = db
    metadata = MetaData()
    users = Table('Users', metadata,
        Column('UserName', String(255), unique=True),
        Column('SaltedPassword', String(255)),
        Column('PasswordSalt', String(255)),
        Column('EncryptedUserId', String(255)),
        Column('UserIdSalt', String(255))
        )

    sessions = Table('Sessions', metadata,
        Column('SessionId', String(255), unique=True),
        Column('UserId', String(255)),
        Column('LastTouched', BigInteger)
        )

    metadata.create_all(self.db_engine)

  def getConn(self):
    return self.db_engine.connect()

  def newUser(self, username, password):
    uid = binascii.hexlify(os.urandom(256/8))

    conn = self.getConn()
    metadata = MetaData(conn)

    users = Table('Users', metadata, autoload=True)
    
    user = User(uid, username, password)

    stmt = users.insert().values(UserName=user.username,
        SaltedPassword=user.salted_password, PasswordSalt=user.password_salt,
        EncryptedUserId=user.encrypted_uid, UserIdSalt=user.uid_salt)

    try:
      result = conn.execute(stmt)
    except IntegrityError:
      raise DuplicateUsernameException()

    conn.close()

    return user

  def writeUser(self, user):
    self.deleteUser(user.username)
    conn = self.getConn()
    metadata = MetaData(conn)

    users = Table('Users', metadata, autoload=True)

    stmt = users.insert().values(UserName=user.username,
        SaltedPassword=user.salted_password, PasswordSalt=user.password_salt,
        EncryptedUserId=user.encrypted_uid, UserIdSalt=user.uid_salt)

    result = conn.execute(stmt)

    conn.close()

  def getUser(self, username):
    conn = self.getConn()
    metadata = MetaData(conn)

    users = Table('Users', metadata, autoload=True)

    stmt = users.select().where(users.c.UserName==username)

    result = conn.execute(stmt)

    row = result.fetchone()

    conn.close()

    if not row:
      return None

    return User(row.EncryptedUserId, row.UserName, row.SaltedPassword,
        row.UserIdSalt, row.PasswordSalt)

  def deleteUser(self, username):
    conn = self.getConn()
    metadata = MetaData(conn)

    users = Table('Users', metadata, autoload=True)

    stmt = users.delete().where(users.c.UserName==username)

    result = conn.execute(stmt)

    conn.close()

    if result.rowcount > 0:
      return True
    return False

  def writeSession(self, session):
    conn = self.getConn()
    metadata = MetaData(conn)

    sessions = Table('Sessions', metadata, autoload=True)

    stmt = sessions.insert().values(SessionId=session.sid, UserId=session.uid,
        LastTouched=session.last_touched)

    try:
      result = conn.execute(stmt)
    except IntegrityError:
      raise DuplicateSessionIdException

    conn.close()

  def getSession(self, sid):
    conn = self.getConn()
    metadata = MetaData(conn)

    sessions = Table('Sessions', metadata, autoload=True)

    stmt = sessions.select().where(sessions.c.SessionId==sid)

    result = conn.execute(stmt)

    row = result.fetchone()

    conn.close()

    if not row:
      return None

    return Session(row.UserId, row.SessionId, row.LastTouched)

  def deleteSession(self, sid):
    conn = self.getConn()
    metadata = MetaData(conn)

    sessions = Table('Sessions', metadata, autoload=True)

    stmt = sessions.delete().where(sessions.c.SessionId==sid)

    result = conn.execute(stmt)

    conn.close()

    if result.rowcount > 0:
      return True

    return False
