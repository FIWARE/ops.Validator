# coding=utf-8
from oslo_config import cfg
CONF = cfg.CONF


def setup_config(app):
    conf_file = "/opt/fiware_validator/etc/bork/%s.conf" % app
    CONF(project=app, args=["--config-file=%s" % conf_file], default_config_files=[conf_file])
