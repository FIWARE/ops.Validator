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
import logging
from git import Repo


class RepoManager:
    """Repository manager for custom recipes"""
    def __init__(self, user):
        self.user = user

    def create(self, name):
        """Create a new repo from name"""
        self.check_credentials()
        repo_full_path = os.path.abspath(name)
        self.repo.init(repo_full_path)

    def delete(self, name):
        """Delete repo from name"""
        self.check_credentials()
        repo_full_path = os.path.abspath(name)
        shutil.rmtree(repo_full_path)

    def check_credentials(self):
        """Check user credentials"""
        if "testbed" in self.user['role'].lower():
            return True
        else:
            logging.warning("Unauthorize repository access for %s" % self.user)
            exit(1)

    def view(self):
        """List repository entries for current user"""
        self.check_credentials()
        tree = self.repo.heads
        return tree

    def archive(self, tar_path):
        """Archive the repository contents to a tar file"""
        self.check_credentials()
        tar_full_path = os.path.abspath(tar_path)
        return repo.archive(open(os.path.join(tar_full_path, "%s.tar" % self.user)), "wb")

if __name__ == '__main__':
    m = RepoManager()
