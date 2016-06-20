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
from bork_api.common.exception import CookbookDeploymentException, CookbookSyntaxException, CookbookInstallException
from bork_api.common.i18n import _LW, _LE, _

LOG = logging.getLogger(__name__)

opts = [
    cfg.StrOpt('cmd_install', default='knife cookbook site install {}'),
    cfg.StrOpt('cmd_config', default='{"run_list": [ "recipe[%s]"]}'),
    cfg.StrOpt('cmd_inject', default="echo '{}' >/etc/chef/solo.json"),
    cfg.StrOpt('cmd_syntax', default='knife cookbook test {}'),
    cfg.StrOpt('cmd_deploy', default='chef-solo –c /etc/chef/solo.rb -j /etc/chef/solo.json'),
]

CONF = cfg.CONF
CONF.register_opts(opts, group="clients_chef")


class ChefClient(object):
    """
    Wrapper for Docker client
    """

    def __init__(self):
        self.container = None
        self.dc = DockerManager()

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
        json_cont = CONF.clients_chef.cmd_config % (cookbook, recipe)
        cmd_inject = CONF.clients_chef.cmd_inject.format(json_cont)
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

    def run_deploy(self, cookbook, recipe, image):
        """ Run cookbook deployment
        :param cookbook: cookbook to deploy
        :return msg: dictionary with results and state
        """
        try:
            # launch execution
            self.dc.container = self.dc.run_container(image)
            cmd_deploy = CONF.clients_chef.cmd_deploy
            resp_launch = self.dc.execute_command(cmd_deploy)
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

    def run_test(self, cookbook, image):
        """ Test cookbook syntax
        :param cookbook: cookbook to test
        :return msg: dictionary with results and state
        """
        try:
            self.dc.container = self.dc.run_container(image)
            cmd_syntax = CONF.clients_chef.cmd_syntax.format(cookbook)
            resp_test = self.dc.execute_command(cmd_syntax)
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

    def run_install(self, cookbook, image):
        """Run download and install command
        :param cookbook: cookbook to process
        :return msg: operation result
        """
        try:
            self.dc.container = self.dc.run_container(image)
            cmd_install = CONF.clients_chef.cmd_install.format(cookbook)
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


if __name__ == '__main__':
    c = ChefClient("tcp://127.0.0.1:2375")
    c.dc.run_container("/etc/bork/chef-trusty.dockerfile")
