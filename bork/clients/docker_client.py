# coding=utf-8
"""
Dockerfile Management
"""
import os
import re
import logging
from oslo_config import cfg

LOG = logging.getLogger(__name__)


class DockerClient:
    """
    Docker Client Object Model
    """

    def __init__(self):
        self.dockerfile_path = cfg.CONF.config_dir

    def list_systems(self):
        """
        List current supported systems
        :return:
        """
        systems = set()
        LOG.debug("Searching supported systems in %s" % self.dockerfile_path)
        for df in os.listdir(self.dockerfile_path):
            if os.path.splitext(df)[1] == ".dockerfile":
                with open(os.path.abspath(df)) as dff:
                    cont = dff.read()
                    m = re.match("FROM ([^:]+):([^:]+)\n", cont)
                    if m:
                        systems.add({m.group(1): m.group(2)})
        return systems
