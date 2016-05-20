#!/usr/bin/python
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

"""
Chef Validator API Server. An OpenStack ReST API to Validate Chef Cookbooks.
"""

import os
import sys
import six
import oslo_i18n as i18n
from oslo_config import cfg
from bork.common import log as logging
from bork.common.i18n import _LI
from bork.common import config
from bork.common import wsgi


def main():
    """Launch validator API """
    try:
        config_dir = "/etc/bork"
        app_name = os.path.splitext(os.path.basename(__file__))[0]
        # default path
        if 'config_dir' not in cfg.CONF:
            sys.argv.append('--config-dir=%s' % config_dir)
        if 'config_file' not in cfg.CONF:
            sys.argv.append('--config-file=%s' %
                            os.path.join(
                                config_dir,
                                "%s.conf" % app_name
                            )
                            )
        i18n.enable_lazy()
        CONF = config.CONF
        config.parse_args()
        logging.setup(CONF, app_name)
        app = config.load_paste_app(app_name)
        port, host = (CONF.bind_port, CONF.bind_host)
        LOG = logging.getLogger()
        LOG.info(_LI('Starting Validator ReST API on %(host)s:%(port)s'),
                 {'host': host, 'port': port})
        server = wsgi.Service(app, port, host)
        server.start()
        server.wait()
    except RuntimeError as e:
        msg = six.text_type(e)
        sys.exit("ERROR: %s" % msg)


if __name__ == '__main__':
    main()
