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

import git
from oslo_config import cfg
from oslo_log import log as logging
from git import Repo

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class RepoManager:
    """User Repository manager for custom recipes"""
    def __init__(self, user):
        self.user = user
        self.full_path = os.path.join(CONF.clients_git.repo_path, user)
        try:
            self.repo = Repo(path=self.full_path)
        except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
            self.repo = self.create()
            self.version = self.repo.version

    def create(self):
        """Create a new repo from name"""
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)
        return Repo.init(self.full_path)

    def delete(self):
        """Delete repo from name"""
        shutil.rmtree(self.full_path)

    def check_credentials(self):
        """Check user credentials"""
        if "community" in self.user['role'].lower():
            return True
        else:
            LOG.warning("Unauthorize repository access for %s" % self.user)
            exit(1)

    def view(self):
        """List repository entries for current user"""
        tree = self.repo.heads.master.commit
        return [f for f in tree]

    def archive(self):
        """Archive the repository contents to a tar file"""
        self.check_credentials()
        return self.repo.archive(open(os.path.join(self.full_path, "%s.tar" % self.user)), "wb")

    def add_cookbook(self, path):
        """
        Adds files from path to user repo
        :param path: local path to add from
        :return: current head version
        """
        shutil.copytree(path, self.full_path)
        self.repo.git.add(A=True)
        self.repo.index.commit("Updated %s" % path)
        return self.repo.index.version

    def browse_file(self, file):
        """Shows file contents"""
        item = None
        tree = self.repo.commit.tree
        for item in tree.traverse():
            if item.type == 'blob' and item.name == file:
                break
        return item

    def browse_repository(self):
        """Shows repository contents"""
        tree = self.repo.commit.tree
        return [c for c in tree]

    def check_branches(self):
        """Shows repository branches"""
        return self.repo.heads

    def check_tags(self):
        """Shows repository tags"""
        return self.repo.tags

    def link_commit(self, message):
        """Commit Repository changes"""
        return self.repo.commit(message)

    def checkout(self, url):
        self.repo.clone_from(url, self.full_path)

    def statistics(self):
        """Show several usage statistics"""
        message = u""
        file_count = 0
        tree_count = 0
        tree = self.repo.commit.tree
        for item in tree.traverse():
            file_count += item.type == 'blob'
            tree_count += item.type == 'tree'

        message += u"files: %d, directories: %d\n" % (len(tree.blobs), len(tree.trees))
        message += u"Current head: %s" % self.repo.heads.master
        return message


if __name__ == '__main__':
    import logging; logging.basicConfig(); LOG.logger.setLevel(logging.DEBUG)
    m = RepoManager("testuser")


