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
import base64
import json
import os
import shutil
import urllib2

from oslo_log import log as logging
from oslo_config import cfg

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class LocalStorage:

    def __init__(self, path=None):
        path = path or CONF.clients_storage.local_path
        self.path = os.path.abspath(path)

    def list_cookbooks(self):
        """
        :return: list of all cookbooks in the current path
        """
        valid = []
        for cb in os.listdir(self.path):
            if self.check_chef_cookbook(cb):
                valid.append({'name': cb, 'system': 'chef'})
            if self.check_puppet_module(cb):
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

    def find_system(self,cb_path):
        """
        Discovers cookbook format from a given path
        :param cb_path: path to the cookbook
        :return: system type
        """
        system = "Unknown"
        if self.check_puppet_module(cb_path):
            system = "puppet"
        elif self.check_chef_cookbook(cb_path):
            system = "chef"
        return system

    def reset(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def download(self, url):
        """
        Download cookbook from a given url
        :param url: repository to download from
        :return: local temp path
        """
        # expected path: r"https://api.github.com/repos/user/project/contents/subpath1/subpath2"
        BASE_API_URL = r"https://api.github.com/repos/"
        repo_path = [x for x in url.split("/") if len(x) > 0]
        repo_user = repo_path[2]
        repo_project = repo_path[3]
        repo_subpath = "/".join(repo_path[repo_path.index("tree") + 2:])
        url = BASE_API_URL + "/".join((repo_user, repo_project, "contents", repo_subpath))
        local_path = os.path.join(self.path, url.split("/")[-1])
        LOG.info("Downloading from %s to %s" % (url, local_path))
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        resp = None, None

        def write_file(item, dir_name):
            name = item['name']
            try:
                res = urllib2.urlopen(item['url']).read()
                coded_string = json.loads(res)['content']
                with open(os.path.join(dir_name, name), 'w') as f:
                    f.write(base64.b64decode(coded_string))
            except urllib2.HTTPError as e:
                LOG.error("File error %s" % e)

        def write_files(url, dir_name):
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            try:
                data = urllib2.urlopen(url).read()
            except urllib2.HTTPError as e:
                LOG.error("Directory error %s" % e)
                return True
            git_dir = json.loads(data)

            for item in git_dir:
                if item['type'] == 'file':
                    write_file(item, dir_name)
                elif item['type'] == 'dir':
                    write_files(item['url'], dir_name=os.path.join(dir_name, item['name']))
            return False

        error = write_files(url, local_path)

        if not error:
            resp = url.split("/")[-1], local_path
        return resp