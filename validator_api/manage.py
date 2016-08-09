#!/usr/bin/env python
# coding=utf-8
import os
import sys

from bork_api.common import config, log

APPNAME = "bork_api"
config.setup_config(APPNAME)
log.setup(APPNAME)

LOG = log.getLogger(__name__)
CONF = config.CONF


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % APPNAME)
    sys.path.insert(1, os.path.abspath('./'))
    from django.core.management import execute_from_command_line
    modded_cmd = sys.argv
    if ":" in sys.argv[-1]:
        modded_cmd = sys.argv[:-1]
        modded_cmd.append("%s:%s" % (CONF.bind_host, CONF.bind_port))
    execute_from_command_line(modded_cmd)
