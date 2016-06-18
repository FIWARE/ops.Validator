# coding=utf-8
from oslo_config import cfg
CONF = cfg.CONF


def setup_config(app):
    CONF(project=app, args=[], default_config_files=["/opt/fiware_validator/etc/bork/%s.conf" % app])
