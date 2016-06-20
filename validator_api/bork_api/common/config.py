# coding=utf-8
import os
from oslo_config import cfg
CONF = cfg.CONF


def setup_config(app):
    conf_file = os.path.abspath("../etc/bork/%s.conf" % app)
    CONF(project=app, args=["--config-file=%s" % conf_file], default_config_files=[conf_file])

