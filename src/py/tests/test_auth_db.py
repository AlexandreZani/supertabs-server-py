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




