#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
""" A very simple example client for Validator Usage"""

import json
import pprint
import os
import sys

import urllib2
from oslo_log import log as logging
from oslo_config import cfg


# simple local logging
LOG = logging.getLogger(__name__)
logging.register_options(cfg.CONF)
cfg.CONF.debug = True
cfg.CONF.logging_default_format_string = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
logging.setup(cfg.CONF, 'validator_client')

# local configuration
opts = [
    cfg.StrOpt('image', help="Docker Image to deploy", default="pmverdugo/chef-ubuntu12"),
    cfg.StrOpt('cookbook', help="Name of the cookbook to deploy", default="wilma"),
    cfg.StrOpt('username', help="Keystone username"),
    cfg.StrOpt('password', help="Keystone password"),
    cfg.StrOpt('system', help="Deployment System", default="chef"),
    cfg.StrOpt('validator_url', help="Chef Validator Url"),
]
cfg.CONF.register_cli_opts(opts)
cfg.CONF(sys.argv[1:])
CONF = cfg.CONF

# default values
USERNAME = os.environ.get('OS_USERNAME', CONF.username)
PASSWORD = os.environ.get('OS_PASSWORD', CONF.password)
VALIDATOR_URL = os.environ.get('Validator_URL', CONF.validator_url)


def client():
    """ Sends a static request based on commandline arguments,
    logs the response """
    if USERNAME is None or PASSWORD is None or VALIDATOR_URL is None:
        raise Exception("Needed valid username, password and validator_url")
    # sample request data
    postdata = {
        "cookbook": CONF.cookbook,
        "image": CONF.image,
        'system': CONF.system
    }
    send_json(VALIDATOR_URL + "/deployments/", postdata)


def send_json(url, postdata):
    # sends the request
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, USERNAME, PASSWORD)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(postdata)
    try:
        response = urllib2.urlopen(req, data)
        data = response.read()
        data = json.loads(data)
    except urllib2.HTTPError as e:
        data = e.read()
    pprint.pprint(data)


def launch():
    send_json(VALIDATOR_URL + "/deployments/%s/launch/" % id, None)

if __name__ == '__main__':
    # step 1
    client()
