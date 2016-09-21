# coding=utf-8
"""
Dockerfile Management
"""
import os
import re

from docker import Client as DC
from docker.errors import NotFound
from oslo_config import cfg
from oslo_log import log as logging
from bork_api.common.i18n import _LW, _LI
from bork_api.common.exception import DockerContainerException

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class DockerManager:
    """
    Docker Manager Object Model
    """

    def __init__(self, path=None, url=None):
        self._url = url or CONF.clients_docker.url
        self.dockerfile_path = path or CONF.clients_docker.build_dir
        self.dc = DC(base_url=self._url)

    def list_images(self):
        """
        List current supported systems
        :return:
        """
        systems = []
        LOG.info("Searching supported systems in %s" % self.dockerfile_path)
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
        status = True
        with open(df) as dockerfile:
            tag = re.findall("(?im)^# tag: (.*)$", dockerfile.read())[0].strip()
            LOG.info("Generating %s from %s" % (tag, df))
        if tag:
            resp = self.dc.build(path=CONF.clients_docker.build_dir, dockerfile=df, rm=True, tag=tag)
            for l in resp:
                if "error" in l.lower():
                    status = False
                LOG.debug(l)
        else:
            status = False
        return status

    def download_image(self, tag):
        status = True
        LOG.info("Downloading image %s" % tag)
        try:
            res = self.dc.pull(tag)
            for l in res:
                LOG.debug(l)
        except Exception as e:
            status = False
            import traceback
            traceback.print_exc()
        return status

    def prepare_image(self, tag):
        """
        Generate image from local file or download if necessary
        :param tag: image tag
        :return: operation status
        """
        status = True
        LOG.info("Preparing Image %s" % tag)
        available_images = [t['RepoTags'][0].split(":")[0] for t in self.dc.images()]
        if tag not in available_images:
            status = self.download_image(tag)
            if not status:
                df = [d['dockerfile'] for d in self.list_images() if d['tag'] == tag][0]
                status = self.generate_image(df)
        return status

    def run_container(self, user, cookbook, image_name):
        """Run and start a container based on the given image
        mounts local cookbook storage path
        :param image_name: image to run
        :return: operation status
        """
        status = True
        self.prepare_image(image_name)
        contname = self.generate_container_name(user, cookbook, image_name)
        try:
            self.remove_container(contname, kill=True)
            container = self.dc.create_container(
                image_name,
                tty=True,
                volumes=[CONF.clients_git.repo_path],
                name=contname
            ).get('Id')
            self.dc.start(container=container)
        except NotFound as e:
            LOG.error(_LW("Image not found: [%s]" % image_name))
            status = False
        except AttributeError as e:
            LOG.error(_LW("Error creating container: [%s]" % e))
            status = False
            # raise DockerContainerException(image=image_name)
        return status

    def remove_container(self, contname, kill=True):
        """destroy container on exit
        :param kill: inhibits removal for testing purposes
        """
        found = self.get_container_by_name(contname)
        if found:
            LOG.info(_LI('Removing old container [%s]' % contname))
            if kill:
                self.dc.remove_container(found, force=True)
            else:
                self.dc.stop(found)

    def execute_command(self, contname, command):
        """ Execute a command in the given container
        :param command:  bash command to run
        :return:  execution result
        """
        bash_txt = "/bin/bash -c \"{}\"".format(command.replace('"', '\\"'))
        exec_txt = self.dc.exec_create(
            container=self.get_container_by_name(contname),
            cmd=bash_txt
        )
        return self.dc.exec_start(exec_txt)

    def get_container_by_name(self, contname):
        """
        :param contname: name or alias of the container to find
        :return: container found
        """
        found = None
        try:
            found = next(c for c in self.dc.containers(all=True) if contname.lower() in c['Names'][0])
        except StopIteration:
            LOG.info(_LI('Container not found for removal [%s]' % contname))
        return found

    @staticmethod
    def generate_container_name(user, cookbook, image_name):
        """
        :param user: user name
        :param cookbook:  cookbook name
        :param image_name: docker image name
        :return: regular generated container name
        """
        return "{}_{}_{}-validate".format(user, cookbook, image_name.replace("/", "_")).lower()

