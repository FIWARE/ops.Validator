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

from bork_api.clients.docker_client import DockerManager
from bork_api.common.exception import CookbookDeploymentException, CookbookSyntaxException, CookbookInstallException
from bork_api.common.i18n import _LW, _LE, _

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def check_murano_spec(rec):
    """
    Checks if the given file is a murano spec
    :param rec: file path
    :return: check result
    """
    return rec.lower().endswith(".yml")


def check_murano_blueprint(bp_path):
    """
    Test if a directory contains a blueprint
    :param bp_path: directory name
    :return: test result
    """
    LOG.info("checking %s" % bp_path)
    check = False
    # check if the item is a directory
    if os.path.isdir(bp_path):
        # check if the item has a specs directory
        if os.path.isdir(os.path.join(bp_path, "specs")):
            check = True
            LOG.debug("blueprint found: %s" % bp_path)
    if not check:
        LOG.debug("Not a blueprint: %s" % bp_path)
    return check


def list_specs(cb_path):
    """
    :return: list of all specs in the current blueprint
    """
    valid = []
    for rec in os.listdir(os.path.join(cb_path, "specs")):
        if check_murano_spec(rec):
            valid.append(rec)
    return valid


class MuranoClient(object):
    """
    Wrapper for Docker client
    """

    def __init__(self):
        self.container = None
        self.dc = DockerManager()

    def blueprint_deployment_test(self, blueprint, spec='default', image='default'):
        """
        Try to process a blueprint and return results
        :param blueprint: blueprint to deploy
        :param spec: spec to deploy
        :param image: image to deploy to
        :return: dictionary with results
        """
        LOG.debug("Sending blueprint to docker server at %s" % self.dc._url)
        b_success = True
        msg = {}
        self.dc.run_container(image)
        msg['install'] = self.run_install(blueprint)
        b_success &= msg['install']['success']
        msg['test'] = self.run_test(blueprint)
        b_success &= msg['test']['success']
        msg['deploy'] = self.run_deploy(blueprint)
        b_success &= msg['deploy']['success']

        # check execution output
        if b_success:
            msg['result'] = {
                'success': True,
                'result': "Blueprint %s successfully deployed\n" % blueprint
            }
        else:
            msg['result'] = {
                'success': False,
                'result': "Error deploying blueprint {}\n".format(blueprint)
            }
            LOG.error(_LW(msg))
        self.dc.remove_container()
        return msg

    def run_deploy(self, blueprint, spec, image):
        """ Run blueprint deployment
        :param blueprint: blueprint to deploy
        :return msg: dictionary with results and state
        """
        try:
            # launch execution
            self.dc.container = self.dc.run_container(image)
            cmd_deploy = CONF.clients_murano.cmd_deploy
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
            LOG.error(_LW("Blueprint deployment exception %s" % e))
            raise CookbookDeploymentException(blueprint=blueprint)
        return msg

    def run_test(self, blueprint, image):
        """ Test blueprint syntax
        :param blueprint: blueprint to test
        :return msg: dictionary with results and state
        """
        try:
            self.dc.container = self.dc.run_container(image)
            cmd_syntax = CONF.clients_murano.cmd_syntax.format(blueprint)
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
            LOG.error(_LW("Blueprint syntax exception %s" % e))
            raise CookbookSyntaxException(blueprint=blueprint)
        return msg

    def run_install(self, blueprint, image):
        """Run download and install command
        :param blueprint: blueprint to process
        :return msg: operation result
        """
        try:
            self.dc.container = self.dc.run_container(image)
            cmd_install = CONF.clients_murano.cmd_install.format(blueprint)
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
            LOG.error(_LW("Murano install exception: %s" % e))
            raise CookbookInstallException(blueprint=blueprint)
        return msg


if __name__ == '__main__':
    c = MuranoClient("tcp://127.0.0.1:2375")
    c.dc.run_container("/etc/bork/murano-trusty.dockerfile")
