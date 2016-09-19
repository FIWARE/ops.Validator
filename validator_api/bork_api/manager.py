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

from oslo_config import cfg
from oslo_log import log as logging

from bork_api.clients.git_client import RepoManager
from bork_api.clients.storage_client import LocalStorage
from bork_api.models import Image, Deployment, Recipe, CookBook


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def images_cleanup():
    """ Cleanup image db"""
    LOG.debug("Cleanup old Images")
    Image.objects.all().delete()


def deployments_cleanup():
    """ Cleanup previous deployments """
    LOG.info("Cleanup old Deployments")
    Deployment.objects.all().delete()


def recipes_cleanup():
    """ Cleanup previous recipes """
    LOG.info("Cleanup old Recipes")
    Recipe.objects.all().delete()


def cookbooks_cleanup():
    """ Cleanup previously downloaded cookbooks """
    LOG.info("Cleanup old Cookbooks")
    CookBook.objects.all().delete()
    LocalStorage().reset()


def cookbooks_add():
    """Add local cookbooks to db"""
    l = LocalStorage()
    for user in l.list_users():
        repo = RepoManager(user)
        for cb in l.list_cookbooks(user):
            system = l.find_system(cb)
            LOG.info("Adding cookbook %s" % cb)
            cb = CookBook()
            cb.name = cb
            cb.system = system
            cb.version = repo.version
            cb.path = os.path.join(l.path, cb)
            cb.user = user
            cb.save()
            for r in l.list_recipes(cb.path):
                ro = Recipe()
                ro.name = r
                ro.cookbook = cb
                ro.version = repo.browse_file(r)
                ro.system = system
                ro.user = user
                ro.save()


def recipes_add():
    """ Add detected recipes based on local cookbooks to db"""
    l = LocalStorage()
    for user in l.list_users():
        repo = RepoManager(user)
        for cb in l.list_cookbooks(user):
            system = l.find_system(cb)
            for r in l.list_recipes(cb):
                ro = Recipe()
                ro.name = r
                ro.cookbook = cb
                ro.version = repo.browse_file(r)
                ro.system = system
                ro.user = user
                ro.save()
