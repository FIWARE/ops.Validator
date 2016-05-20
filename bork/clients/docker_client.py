# coding=utf-8
"""
Dockerfile Management
"""
import logging
from oslo_config import cfg


class DockerClient:
    """
    Docker Client Object Model
    """

    def __init__(self):
        self.dockerfile_path = cfg.CONF.config_dir

    def list_systems(self):
        return self.dockerfile_path
