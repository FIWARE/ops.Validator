# coding=utf-8
"""
Dockerfile Management
"""
import logging
import re
import os
from docker import Client as DC
from oslo_config import cfg


CONF = cfg.CONF
CONF.register_opt(cfg.StrOpt('config_dir', default="/etc/bork"))
CONF.register_opt(cfg.StrOpt('url', default="tcp://127.0.0.1:2375"), group="clients_docker")
LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class DockerManager:
    """
    Docker Manager Object Model
    """

    def __init__(self, path="/etc/bork"):
        self.dockerfile_path = path

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

