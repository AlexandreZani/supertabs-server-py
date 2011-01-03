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

    creds = CredentialsFactory.getCredentials(cred_type, cred_args, adb)

    request = RequestFactory.getRequest("Login", {}, creds)

    response = request.execute(sdb)

    assert 256/8*2 == len(response["credentials"]["args"]["sid"])







