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
""" Main action mapper"""

from oslo_log import log as logging
from oslo_config import cfg
from webob import exc

from bork.common import wsgi
from bork.common.i18n import _LI, _
import bork.common.utils
from bork.engine.validate import ValidateEngine
from bork.engine.CookBook import CookBookEngine
from bork.engine.System import SystemEngine

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class PuppetController(object):
    """
    Puppet Controller Object
    Implements Application logic
    """

    @staticmethod
    def validate(request, body):
        """ Validate the given cookbook
        :param request: request context
        :param body: a json with deployment parameters
        :return : a json file with process results
        """
        body = body or {}
        if len(body) < 1:
            raise exc.HTTPBadRequest(_("No action specified"))
        try:
            cookbook = body['cookbook']
            image = body['image']
        except KeyError:
            raise exc.HTTPBadRequest(_("Insufficient payload"))

        LOG.info(_LI('Processing Request for cookbook %s, image %s' % (cookbook, image)))
        res = ValidateEngine().validate_puppet_cookbook(cookbook, image, request)
        return res


class ChefController(object):
    """
    Chef Controller Object
    Implements Application logic
    """

    @staticmethod
    def validate(request, body):
        """ Validate the given cookbook
        :param request: request context
        :param body: a json with deployment parameters
        :return : a json file with process results
        """
        body = body or {}
        if len(body) < 1:
            raise exc.HTTPBadRequest(_("No action specified"))
        try:
            cookbook = body['cookbook']
            image = body['image']
        except KeyError:
            raise exc.HTTPBadRequest(_("Insufficient payload"))

        LOG.info(_LI('Processing Request for cookbook %s, image %s' % (cookbook, image)))
        res = ValidateEngine().validate_chef_cookbook(cookbook, image, request)
        return res


class CookBooksController(object):
    """
    Cookbook Controller Object
    Implements Application logic
    """

    @staticmethod
    def list():
        """ List available cookbooks

        :return : a json file with process results
        """
        LOG.info(_LI('Processing Request for list cookbooks'))
        res = CookBookEngine().list()
        return res


class SystemsController(object):
    """
    Cookbook Controller Object
    Implements Application logic
    """

    @staticmethod
    def list():
        """ List available systems
        :return : a json file with process results
        """
        LOG.info(_LI('Processing Request for list systems'))
        res = SystemEngine().list()
        return res


def create_chef_resource():
    """
    Actions chef factory method.
    """
    deserializer = bork.common.utils.JSONDeserializer()
    serializer = bork.common.utils.JSONSerializer()
    return wsgi.Resource(ChefController(), deserializer, serializer)


def create_puppet_resource():
    """
    Actions puppet factory method.
    """
    deserializer = bork.common.utils.JSONDeserializer()
    serializer = bork.common.utils.JSONSerializer()
    return wsgi.Resource(PuppetController(), deserializer, serializer)


def create_cookbooks_resource():
    deserializer = bork.common.utils.JSONDeserializer()
    serializer = bork.common.utils.JSONSerializer()
    return wsgi.Resource(CookBooksController(), deserializer, serializer)


def create_systems_resource():
    return wsgi.Resource(SystemsController())
