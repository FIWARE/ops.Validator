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
                        systems.append({'name': m.group(1), 'version': m.group(2), 'dockerfile': image_path, 'system': system})
        return systems
