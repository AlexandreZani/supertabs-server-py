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
from jinja2 import Environment, PackageLoader
from cgi import parse_qs, escape
from os import urandom
from binascii import hexlify, unhexlify
from sqlalchemy import *

jinja_env = Environment(loader=PackageLoader('supertabs.web', 'templates'))

def api(environ, start_response):
  try:
    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  except ValueError:
    request_body_size = 0

  request_body = environ['wsgi.input'].read(request_body_size)

  try:
    request = request_factory.parseRequest(request_body,
      auth_db=environ["auth_db"], credentials_factory=credentials_factory)

    response = request.execute(environ["supertabs_db"])
  except RequestError or CredentialsError, (ex):
    response = { "error" : str(ex.__class__.__name__) }

  response_txt = json.dumps(response)

  start_response('200 OK', [('Content-type','application/json')])

  return [response_txt]

def not_found(environ, start_response):
  start_response('404 Not Found', [('Content-type','text/html')])
  return [environ["PATH_INFO"] + " Not Found"]

def new_user(environ, start_response):
  try:
    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  except ValueError:
    request_body_size = 0

  request_body = environ['wsgi.input'].read(request_body_size)

  out_params = {}

  in_params = parse_qs(request_body)
  try:
    out_params["username"] = in_params["username"][0]
    
    user = environ["auth_db"].getUser(in_params["username"][0])
    try:
      environ["auth_db"].newUser(in_params["username"][0], in_params["password"][0])
      out_params["success"] = True
    except DuplicateUsernameException:
      out_params["duplicate_username"] = True
  except KeyError:
    out_params = {}


  start_response('200 OK', [('Content-type','text/html')])
  template = jinja_env.get_template('new_user_form.html')

  return [str(template.render(out_params))]
