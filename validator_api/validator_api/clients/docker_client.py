# coding=utf-8
"""
Dockerfile Management
"""
import logging
import os
import re

from docker import Client as DC
from docker.errors import NotFound
from oslo_config import cfg

from validator_api.common.i18n import _LW, _LI
from validator_api.common.exception import DockerContainerException

CONF = cfg.CONF
CONF.register_opt(cfg.StrOpt('config_dir', default="/etc/bork"))
CONF.register_opt(cfg.StrOpt('url', default="tcp://127.0.0.1:2375"), group="clients_docker")
LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class DockerManager:
    """
    Docker Manager Object Model
    """

    def __init__(self, path="/etc/bork", url=CONF.clients_docker.url):
        self._url = url
        self.dockerfile_path = path
        self.dc = DC(base_url=self._url)

    def list_systems(self):
        """
        List current supported systems
        :return:
        """
        systems = []
        LOG.debug("Searching supported systems in %s" % self.dockerfile_path)
        for df in os.listdir(self.dockerfile_path):
            image_path = os.path.join(self.dockerfile_path, df)
            system = df.split("-")[0]
            if os.path.splitext(df)[1] == ".dockerfile":
                with open(image_path) as dff:
                    cont = dff.read()
                    m = re.search("FROM ([^:]+):([^\n]+)\n", cont)
                    if m:
                        tag = re.findall("(?im)^# tag: (.*)$", cont)[0].strip()
                        systems.append({'name': m.group(1), 'version': m.group(2), 'dockerfile': image_path, 'system': system, 'tag': tag})
        return systems

    def generate_image(self, df):
        """generate docker image"""
        status = False
        dc = DC(base_url=CONF.clients_docker.url)
        dc.info()
        with open(df) as dockerfile:
            tag = re.findall("(?im)^# tag: (.*)$", dockerfile.read())[0].strip()
            LOG.debug("Generating %s from %s" % (tag, df))
        if tag:
            resp = dc.build(
                path=CONF.config_dir,
                dockerfile=df,
                rm=True,
                tag=tag
            )
        for l in resp:
            if "error" in l.lower():
                status = False
            LOG.debug(l)
        return status

    def download_image(self, tag):
        status = True
        dc = DC(base_url=CONF.clients_docker.url)
        resp = dc.pull(tag)
        for l in resp:
            if "error" in l.lower():
                status = False
            LOG.debug(l)
        return status

    def run_container(self, image_name):
        """Run and start a container based on the given image
        :param image: image to run
        :return:
        """
        contname = "{}-validate".format(image_name).replace("/", "_")
        try:
            try:
                self.remove_container(contname, force=True)
                LOG.info(_LI('Removing old %s container' % contname))
            except NotFound:
                pass
            self.container = self.dc.create_container(
                image_name,
                tty=True,
                name=contname
            ).get('Id')
            self.dc.start(container=self.container)
        except NotFound as e:
            LOG.error(_LW("Image not found: %s" % image_name))
        except AttributeError as e:
            LOG.error(_LW("Error creating container: %s" % e))
            raise DockerContainerException(image=image_name)

    def remove_container(self, kill=True):
        """destroy container on exit
        :param kill: inhibits removal for testing purposes
        """
        self.dc.stop(self.container)
        if kill:
            self.remove_container(self.container)

    def execute_command(self, command):
        """ Execute a command in the given container
        :param command:  bash command to run
        :return:  execution result
        """
        bash_txt = "/bin/bash -c \"{}\"".format(command.replace('"', '\\"'))
        exec_txt = self.dc.exec_create(
            container=self.container,
            cmd=bash_txt
        )
        return self.dc.exec_start(exec_txt)