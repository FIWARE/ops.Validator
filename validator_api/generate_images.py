#!/usr/bin/env python
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

"""Helper tool to generate valid test images in docker format"""

import logging
import sys
import os
from docker import Client as DockerClient
from oslo_config import cfg
import re

CONF = cfg.CONF
CONF.register_opt(cfg.StrOpt('config_dir', default="/etc/bork"))
CONF.register_opt(cfg.StrOpt('url', default="tcp://127.0.0.1:2375"), group="clients_docker")
LOG = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def dock_image(dockerfile_path):
    """generate docker image"""
    status = True
    dc = DockerClient(base_url=CONF.clients_docker.url)
    dc.info()
    with open(dockerfile_path) as dockerfile:
        tag = re.findall("(?im)^# tag: (.*)$", dockerfile.read())[0].strip()
        LOG.debug("Generating %s from %s" % (tag, dockerfile_path))
    if tag:
        resp = dc.build(
            path=os.path.dirname(dockerfile_path),
            dockerfile=os.path.basename(dockerfile_path),
            rm=True,
            tag=tag
        )
        for l in resp:
            if "error" in l.lower():
                status = False
            LOG.debug(l.strip())
    return status


def dock_upload_image(tag):
    status = True
    dc = DockerClient(base_url=CONF.clients_docker.url)
    resp = [line for line in dc.push(tag, stream=True)]
    for l in resp:
        if "error" in l.lower():
            status = False
        LOG.debug(l.strip())
    return status


def dock_images(wp, upload=False):
    """find dockerfiles in config dir"""
    LOG.info("Generating Images...")
    for df in os.listdir(wp):
        if df.endswith(".dockerfile"):
            LOG.info("Generating Image for %s" % df)
            dockerfile_path = os.path.join(wp, df)
            ok = dock_image(dockerfile_path)
            if ok and upload:
                with open(dockerfile_path) as dockerfile:
                    tag = re.findall("(?im)^# tag: (.*)$", dockerfile.read())[0].strip()
                    LOG.info("Uploading image %s" % tag)
                dock_upload_image(tag)


def main(images_dir=CONF.config_dir, upload=False):
    """Generates a Docker Image of test environments based on a local dockerfile."""
    # inject config files dir to syspath
    wp = os.path.abspath(images_dir)
    sys.path.insert(0, wp)
    os.chdir(wp)
    dock_images(wp, upload=upload)

if __name__ == '__main__':
    # include arg --config-dir={configpath}
    main(images_dir="../etc/bork", upload=True)
