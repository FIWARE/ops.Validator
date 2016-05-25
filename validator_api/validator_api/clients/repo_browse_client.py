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


class RepoBrowser:
    def __init__(self, repo):
        """
        Instantiates a repository browser object
        :param repo: RepoManager object
        """
        self.repo = repo

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
    m = RepoBrowser()