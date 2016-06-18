# coding=utf-8
"""
Cookbook Repository Management
"""
from oslo_log import log as logging
import svn.remote

LOG = logging.getLogger(__name__)


class SVNRepo:
    """
    Cookbook Repository Object Model
    """

    def __init__(self, url, user="default", pwd="default", ):
        """
        Connects to a remote svn server
        :param user: username
        :param pwd: password
        :param url: url
        """
        self.r = svn.remote.RemoteClient(url, username=user, password=pwd)
        import pprint; pprint.pprint(self.r.run_command("info", [self.r.url, "--trust-server-cert"]))
        self.version = self.get_version()

    def list_cookbooks(self, rp=None):
        """
        :return: List of all cookbooks in repo
        """
        cookbooks = []
        entries = self.r.list(rel_path=rp)
        for filename in entries:
            if self.check_cookbook(filename):
                cookbooks.append(filename.replace("/", ""))
        return cookbooks

    def check_cookbook(self, name):
        """check if the item is a cookbook"""
        logging.info("checking %s" % name)
        check = False
        # check if the item is a directory
        res = self.info(rel_path=name)
        if res['entry_kind'] == 'dir':
            # check if the item has a recipes directory
            if "recipes/" in self.r.list(rel_path=name):
                check = True
                logging.debug("Cookbook found: %s" % name)
        if not check:
            logging.debug("Not a cookbook: %s" % name)
        return check

    def download_cookbooks(self, local_path='/tmp/cookbooks'):
        """
        Downloads all remote cookbooks to a local path
        :param local_path: path to download to
        :return: operation result
        """
        return self.r.run_command("export", [self.r.url, local_path, "--trust-server-cert", "--force"])

    def info(self, rel_path=None):
        return self.r.info(rel_path=rel_path)

    def get_version(self):
        vers = 'Unknown'
        for l in self.r.run_command("info", [self.r.url, "--trust-server-cert"]):
            if "Revision:" in l:
                vers = l.split(":")[1].strip()
        return vers


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    c = SVNRepo(*sys.argv[1:])
    print c.list_cookbooks()
    c.download_cookbooks()

