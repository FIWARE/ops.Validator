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
import logging


class CookbookRepo:

    def __init__(self, path="/cookbooks"):
        self.path = os.path.abspath(path)

    def list_cookbooks(self):
        """
        :return: list of all cookbooks in the current path
        """
        valid = []
        for cb in os.listdir(self.path):
            if self.check_cookbook(cb):
                valid.append(os.path.join(self.path, cb))
        return valid

    def check_cookbook(self, cb):
        """
        Test if a directory contains a cookbook
        :param cb: directory name
        :return: test result
        """
        logging.info("checking %s" % cb)
        check = False
        # check if the item is a directory
        if os.path.isdir(cb):
            # check if the item has a recipes directory
            if "recipes" in os.listdir(cb) and os.path.isdir(os.path.join(cb, "recipes")):
                check = True
                logging.debug("Cookbook found: %s" % cb)
        if not check:
            logging.debug("Not a cookbook: %s" % cb)
        return check

if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    c = CookbookRepo(*sys.argv[1])
    print c.list_cookbooks()