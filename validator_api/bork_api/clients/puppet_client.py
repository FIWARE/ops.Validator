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

from docker.errors import DockerException
from oslo_config import cfg
from oslo_log import log as logging

from bork_api.clients.docker_client import DockerManager
from bork_api.common.exception import CookbookSyntaxException, \
    CookbookDeploymentException, \
    CookbookInstallException
from bork_api.common.i18n import _LW, _LE, _

LOG = logging.getLogger(__name__)

opts = [
    cfg.StrOpt('url'),
    cfg.StrOpt('image'),
]
CONF = cfg.CONF
CONF.register_opts(opts, group="clients_puppet")


class PuppetClient(object):
    """
    Wrapper for Docker client
    """

    def __init__(self, url=CONF.clients_docker.url):
        self._url = url
        self.container = None
        try:
            self.dc = DockerManager(url=self._url)
        except DockerException as e:
            LOG.error(_LE("Docker client error: %s") % e)
            raise e

    def cookbook_deployment_test(self, cookbook, recipe='default', image='default'):
        """
        Try to process a cookbook and return results
        :param cookbook: cookbook to deploy
        :param recipe: recipe to deploy
        :param image: image to deploy to
        :return: dictionary with results
        """
        LOG.debug("Sending cookbook to docker server in %s" % self._url)
        b_success = True
        msg = {}
        self.dc.run_container(image)
        # inject custom solo.json/solo.rb file
        json_cont = CONF.clients_puppet.cmd_config % (cookbook, recipe)
        cmd_inject = CONF.clients_puppet.cmd_inject.format(json_cont)
        self.dc.execute_command(cmd_inject)

        msg['install'] = self.run_install(cookbook)
        b_success &= msg['install']['success']
        msg['test'] = self.run_test(cookbook)
        b_success &= msg['test']['success']
        msg['deploy'] = self.run_deploy(cookbook)
        b_success &= msg['deploy']['success']

        # check execution output
        if b_success:
            msg['result'] = {
                'success': True,
                'result': "Cookbook %s successfully deployed\n" % cookbook
            }
        else:
            msg['result'] = {
                'success': False,
                'result': "Error deploying cookbook {}\n".format(cookbook)
            }
            LOG.error(_LW(msg))
        self.dc.remove_container()
        return msg

    def run_deploy(self, cookbook):
        """ Run cookbook deployment
        :param cookbook: cookbook to deploy
        :return msg: dictionary with results and state
        """
        try:
            # launch execution
            cmd_launch = CONF.clients_puppet.cmd_launch
            resp_launch = self.dc.execute_command(cmd_launch)
            msg = {
                'success': True,
                'response': resp_launch
            }
            LOG.debug(_("Launch result: %s") % resp_launch)
            if resp_launch is None or "FATAL" in resp_launch:
                msg['success'] = False
        except Exception as e:
            self.dc.remove_container(self.container)
            LOG.error(_LW("Cookbook deployment exception %s" % e))
            raise CookbookDeploymentException(cookbook=cookbook)
        return msg

    def run_test(self, cookbook):
        """ Test cookbook syntax
        :param cookbook: cookbook to test
        :return msg: dictionary with results and state
        """
        try:
            cmd_test = CONF.clients_puppet.cmd_test.format(cookbook)
            resp_test = self.dc.execute_command(cmd_test)
            msg = {
                'success': True,
                'response': resp_test
            }
            for line in resp_test.splitlines():
                if "ERROR" in line:
                    msg['success'] = False
            LOG.debug(_("Test result: %s") % resp_test)
        except Exception as e:
            self.dc.remove_container(self.container)
            LOG.error(_LW("Cookbook syntax exception %s" % e))
            raise CookbookSyntaxException(cookbook=cookbook)
        return msg

    def run_install(self, cookbook):
        """Run download and install command
        :param cookbook: cookbook to process
        :return msg: operation result
        """
        try:
            cmd_install = CONF.clients_puppet.cmd_install.format(cookbook)
            resp_install = self.dc.execute_command(cmd_install)
            msg = {
                'success': True,
                'response': resp_install
            }
            for line in resp_install.splitlines():
                if "ERROR" in line:
                    msg['success'] = False
            LOG.debug(_("Install result: %s") % resp_install)
        except Exception as e:
            self.dc.remove_container(self.container)
            LOG.error(_LW("Chef install exception: %s" % e))
            raise CookbookInstallException(cookbook=cookbook)
        return msg