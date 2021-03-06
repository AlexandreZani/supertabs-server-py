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

from supertabs.requests import *
from supertabs.credentials import *
from supertabs.auth_db import *
from supertabs.supertabs_db import *
import json
from os import path 
import ConfigParser
from supertabs.web import views
import re

# Change this path to wherever you store your configuration file
config_path = "/etc/supertabs/supertabs.conf"

# How to handle views
view_paths = [
    (r"^/api/$", views.api),
    (r"^/new_user/$", views.new_user)
    ]

view_paths = map(lambda view_path: (re.compile(view_path[0]), view_path[1]), view_paths)

# Default values for configurable options
auth_db_url = "mysql://test:password@localhost/SupertabsDB"
supertabs_db_url = "mysql://test:password@localhost/SupertabsDB"

if path.exists(config_path):
  config = ConfigParser.RawConfigParser()
  config.readfp(open(config_path))

  supertabs_db_url = config.get("supertabs_db", "type") + "://"
  supertabs_db_url += config.get("supertabs_db", "username")
  supertabs_db_url += ":" + config.get("supertabs_db", "password")
  supertabs_db_url += "@" + config.get("supertabs_db", "location")
  supertabs_db_url += "/" + config.get("supertabs_db", "database")

  auth_db_url = config.get("auth_db", "type") + "://"
  auth_db_url += config.get("auth_db", "username")
  auth_db_url += ":" + config.get("auth_db", "password")
  auth_db_url += "@" + config.get("auth_db", "location")
  auth_db_url += "/" + config.get("auth_db", "database")

class Application(object):
  def __init__(self, auth_db, supertabs_db):
    self.auth_db = SQLAlchemyAuthDB(create_engine(auth_db, pool_recycle=7200))
    self.supertabs_db = SQLAlchemySupertabsDB(create_engine(supertabs_db, pool_recycle=7200))

  def __call__(self, environ, start_response):
    environ["supertabs_db"] = self.supertabs_db
    environ["auth_db"] = self.auth_db

    if environ["PATH_INFO"][-1] != "/":
      environ["PATH_INFO"] += "/"

    for (regex, handler) in view_paths:
      if regex.search(environ["PATH_INFO"]):
        return handler(environ, start_response)

    return views.not_found(environ, start_response)

application = Application(auth_db_url, supertabs_db_url)

