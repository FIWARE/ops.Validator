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

import os
import shutil
from oslo_log import log as logging
from oslo_config import cfg

LOG = logging.getLogger(__name__)
opts = [
    cfg.StrOpt('path'),
]
CONF = cfg.CONF
CONF.register_opts(opts, group="clients_storage")


class LocalStorage:

    def __init__(self, path=None):
        path = path or CONF.clients_storage.path
        self.path = os.path.abspath(path)

    def list_cookbooks(self):
        """
        :return: list of all cookbooks in the current path
        """
        valid = []
        for cb in os.listdir(self.path):
            if self.check_chef_cookbook(cb):
                valid.append({'name': cb, 'system': 'chef'})
            elif self.check_puppet_module(cb):
                valid.append({'name': cb, 'system': 'pupp'})
        return valid

    def list_recipes(self, cb_path):
        """
        :return: list of all recipes in the current cookbook
        """
        valid = []
        for rec in os.listdir(os.path.join(cb_path, "recipes")):
            if self.check_chef_recipe(rec):
                valid.append(rec)
            elif self.check_puppet_recipe(rec):
                valid.append(rec)
        return valid

    def check_chef_recipe(self, rec):
        return rec.endswith(".rb")

    def check_puppet_recipe(self, rec):
        return rec.endswith(".pp")

    def check_chef_cookbook(self, cb):
        """
        Test if a directory contains a cookbook
        :param cb: directory name
        :return: test result
        """
        LOG.info("checking %s" % cb)
        check = False
        # check if the item is a directory
        cb_path = os.path.join(self.path, cb)
        if os.path.isdir(cb_path):
            # check if the item has a recipes directory
            if os.path.isdir(os.path.join(cb_path, "recipes")):
                check = True
                LOG.debug("Cookbook found: %s" % cb)
        if not check:
            LOG.debug("Not a cookbook: %s" % cb)
        return check

    def check_puppet_module(self, cb):
        """
        Test if a directory contains a cookbook
        :param cb: directory name
        :return: test result
        """
        LOG.info("checking %s" % cb)
        check = False
        # check if the item is a directory
        cb_path = os.path.join(self.path, cb)
        if os.path.isdir(cb_path):
            # check if the item has a manifest directory
            if os.path.isdir(os.path.join(cb_path, "manifest")):
                check = True
                LOG.debug("Module found: %s" % cb)
        if not check:
            LOG.debug("Not a module: %s" % cb)
        return check
    
    def reset(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            os.mkdir(self.path)