# coding=utf-8
"""
Cookbook Repository Management
"""
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
        svn_repo = 'https://{user}:{pwd}@{url}'.format(
            user=user,
            pwd=pwd,
            url=url
        )
        print svn_repo
        self.r = svn.remote.RemoteClient(svn_repo)

    def list_cookbooks(self):
        """
        :return: List of all cookbooks in repo
        """
        cookbooks = []
        entries = self.r.list()
        for filename in entries:
            print filename
            cookbooks.append(filename)
        return cookbooks

    def download_cookbooks(self, local_path='/tmp/cookbooks'):
        """
        Downloads all remote cookbooks to a local path
        :param local_path: path to download to
        :return: operation result
        """
        return self.r.export(local_path)

    def info(self):
        return self.r.info()

if __name__ == '__main__':
    import sys
    c = CookbookRepo(*sys.argv[1:])
    print c.info()
    c.list_cookbooks()
