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

from supertabs.credentials import *
from tests.mock_auth_db import *

def pytest_generate_tests(metafunc):
  if 'db' in metafunc.funcargnames:
    metafunc.addcall(param=1)

def pytest_funcarg__db(request):
  if request.param == 1:
    return MockAuthDB()

class TestUsernamePasswordCreds(object):
  def test_normalOp(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)

    method = "UsernamePassword"
    args = {"username":"username",
        "password":"password"}

    creds = CredentialsFactory.getCredentials(method, args, db)

    assert creds.validateCredentials()

  def test_wrongPassword(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)

    method = "UsernamePassword"
    args = {"username":"username",
        "password":"pasadssword"}

    creds = CredentialsFactory.getCredentials(method, args, db)

    try:
      creds.validateCredentials()
    except InvalidCredentials:
      assert True
    else:
      assert False

  def test_noPassword(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)

    method = "UsernamePassword"
    args = {"username":"username"}

    creds = CredentialsFactory.getCredentials(method, args, db)

    try:
      creds.validateCredentials()
    except InvalidCredentials:
      assert True
    else:
      assert False

  def test_wrongUsername(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)

    method = "UsernamePassword"
    args = {"username":"usesdasdrname",
        "password":"password"}

    creds = CredentialsFactory.getCredentials(method, args, db)

    try:
      creds.validateCredentials()
    except InvalidCredentials:
      assert True
    else:
      assert False

  def test_noUsername(self, db):
    uid = "f3cd95813bfcc2c0cba45a8ee35ba166f4e47052d06e49c628d69a64c30b2b62"
    user = User(uid, "username", "password")

    db.writeUser(user)

    method = "UsernamePassword"
    args = {"password":"password"}

    creds = CredentialsFactory.getCredentials(method, args, db)

    try:
      creds.validateCredentials()
    except InvalidCredentials:
      assert True
    else:
      assert False
