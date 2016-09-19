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

from bork_api.clients import chef_client, puppet_client, murano_client

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class LocalStorage:

    def __init__(self, path=None):
        path = path or CONF.clients_storage.local_path
        self.path = os.path.abspath(path)

    def list_users(self):
        """
        :return: list of all users in the storage path
        """
        users = []
        for us in os.listdir(self.path):
            us = os.path.join(self.path, us)
            users.append(us)
        return users

    def list_cookbooks(self, user):
        """
        :return: list of all cookbooks in the storage path
        """
        valid = []
        for cb in os.listdir(os.path.join(self.path, user)):
            cb = os.path.join(self.path, cb)
            system = self.find_system(cb)
            if system:
                valid.append(cb)
        return valid

    def list_recipes(self, cb):
        """
        Lists available recipes in given cookbook
        :param cb: cookbook path
        :return: list of recipes
        """
        valid = []
        system = self.find_system(cb)
        if system == "chef":
            valid = chef_client.list_recipes(cb)
        elif system == "puppet":
            valid = puppet_client.list_classes(cb)
        elif system == "murano":
            valid == murano_client.list_specs(cb)
        return valid

    @staticmethod
    def find_system(cb_path):
        """
        Discovers cookbook format from a given path
        :param cb_path: path to the cookbook
        :return: system type
        """
        system = None
        if puppet_client.check_puppet_module(cb_path):
            system = "puppet"
        elif chef_client.check_chef_cookbook(cb_path):
            system = "chef"
        elif murano_client.check_murano_blueprint(cb_path):
            system = "murano"
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