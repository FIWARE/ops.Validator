# coding=utf-8
"""
Cookbook Repository Management
"""
import logging
import svn.remote


class CookbookRepo:
    """
    Cookbook Repository Object Model
    """

    def __init__(self, user, pwd, url):
        """
        Connects to a remote svn server
        :param user: username
        :param pwd: password
        :param url: url
        """
        if url.startswith("https://"):
            svn_repo = url
        else:
            svn_repo = 'https://{user}:{pwd}@{url}'.format(
                user=user,
                pwd=pwd,
                url=url
            )
        self.r = svn.remote.RemoteClient(svn_repo)

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
        return self.r.export(local_path)

    def info(self, rel_path=None):
        return self.r.info(rel_path=rel_path)

if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    c = CookbookRepo(*sys.argv[1:])
    print c.list_cookbooks()
    c.download_cookbooks()

