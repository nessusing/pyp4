import os

from .p4core import p4run, p4
from .p4changelist import changelist_payload_fetcher, P4Changelist

class P4Pending(object):
    
    """
    This class provide basic services similar to the Pending tab
    in P4V.
    """

    def __init__(self, user=None, workspace=None):
        """
        user: Perforce user name. None defaults to current user saved in `p4 info`.
        workspace: Perforce clientspec name. None defaults to current client save in `p4 info`.
        """
        if user is None:
            self.__user = p4.user
        else:
            self.__user = user
        if workspace is None:
            self.__client = p4.client
        else:
            self.__client = workspace

        self.__changes = []

        self.fetch()

    @property
    def user(self):
        """
        User name.
        """
        return self.__user

    @user.setter
    def user(self, u):
        """
        Do not forget to call fetch() if user or/and client are updated.
        """
        self.__user = u

    @property
    def workspace(self):
        """
        Clientspec name.
        """
        return self.__client

    @property
    def workspace(self, w):
        """
        Do not forget to call fetch() if user or/and client are updated.
        """
        self.__client = w

    @property
    def changes(self):
        """
        List of changelists within user and client combo.
        """
        return self.__changes

    def __iter__(self):
        """
        Make this class iterable.
        yield: P4Changelist object.
        """
        for payload in changelist_payload_fetcher(self.__changes):
            change = P4Changelist(-1)
            change.load(payload)
            yield change

    def fetch(self):
        """"
        This method updates the pending changelists by fetching P4 api calls 
        to Perforce server.
        This method generally needs to be invoked every time user and/or client
        are updated.
        """
        self.__changes = [c['change'] for c in p4run('changes', '-u', self.__user, '-c', self.__client, '-s', 'pending')]
        self.__changes.append('default')

    def __str__(self):
        """
        String representation of the pending changelist class.
        """
        _str = []
        for c in self.__changes:
            _str.append(str(c))
        _str.append('')
        return os.linesep.join(_str)

    def dump(self):
        """
        Print the string representation of the pending changelist class.
        """
        print(self)



