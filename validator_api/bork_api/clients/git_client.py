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

from git import exc as GitException
from oslo_config import cfg
from oslo_log import log as logging
from git import Repo

from bork_api.clients import chef_client, puppet_client, murano_client

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class RepoManager:
    """User Repository manager for custom recipes"""
    def __init__(self, user):
        self.user = user
        self.full_path = os.path.join(CONF.clients_git.repo_path, user)
        try:
            self.repo = Repo(path=self.full_path)
        except (GitException.InvalidGitRepositoryError, GitException.NoSuchPathError):
            self.repo = self.create()

    def create(self):
        """Create a new repo from name"""
        LOG.info("Creating new repo in %s" % self.full_path)
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
        :return: current path and head version
        """
        cb_path = os.path.join(self.full_path, os.path.basename(path))
        if os.path.exists(cb_path):
         shutil.rmtree(cb_path)
        shutil.copytree(path, cb_path)
        com = self.repo.git.add(A=True)
        self.repo.index.add(com)
        self.repo.index.commit("Updated %s" % path)
        self.version = self.repo.head.commit.tree.hexsha
        LOG.info("Commited at version %s" % self.version)
        return cb_path, self.repo.index.version

    def browse_file(self, file):
        """
        Returns sha1 index of file in repo
        :param file: file path
        :return: current file version id
        """
        item = None
        tree = self.repo.head.commit.tree
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

    def upload_coobook(self, path):
        """
        Uploads a validated cookbook to the official Github repo
        :param path: cookbook path
        :return: status message
        """
        dest_url = None
        if chef_client.check_chef_cookbook(path):
            dest_url = CONF.clients_chef.github_url
        elif puppet_client.check_puppet_module(path):
            dest_url = CONF.clients_puppet.github_url
        elif murano_client.check_murano_blueprint(path):
            dest_url = CONF.clients_murano.github_url
        if dest_url:
            LOG.info("Pushing cookbook to %s" % dest_url)
            dest = self.repo.create_remote(self.user, dest_url)
            self.repo.create_head('remote', dest.refs.master).set_tracking_branch(dest.refs.master)
            message = dest.push()
        else:
            LOG.warning("Error detecting cookbook type for %s" % path)
            message = "Error"
        return message

if __name__ == '__main__':
    import logging; logging.basicConfig(); LOG.logger.setLevel(logging.DEBUG)
    from bork_api.common import config




