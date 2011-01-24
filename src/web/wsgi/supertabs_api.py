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
from os.path import exists
import ConfigParser

# Change this path to wherever you store your configuration file
config_path = "/etc/supertabs/supertabs.conf"

# Default values for configurable options
auth_db_url = "mysql://test:password@localhost/SupertabsDB"
supertabs_db_url = "mysql://test:password@localhost/SupertabsDB"

if exists(config_path):
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

class Api(object):
  def __init__(self, auth_db, supertabs_db):
    self.auth_db = SQLAlchemyAuthDB(create_engine(auth_db))
    self.supertabs_db = SQLAlchemySupertabsDB(create_engine(supertabs_db))

  def __call__(self, environ, start_response):
    try:
      request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
      request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)

    try:
      request = request_factory.parseRequest(request_body, auth_db=self.auth_db,
          credentials_factory=credentials_factory)

      response = request.execute(self.supertabs_db)
    except RequestError or CredentialsError, (ex):
      response = { "Error" : str(ex.__class__.__name__) }

    response_txt = json.dumps(response)

    start_response('200 OK', [('Content-type','application/json')])

    return [response_txt]

application = Api(auth_db_url, supertabs_db_url)
