import os
import types
from collections import defaultdict

from .p4core import p4run, P4Exception, p4, tolist, p4sync, is_depot_path


def file_payload_fetcher(files):
    """
    Execute 'fstat' command in batch mode. Firing a single command against many files
    greatly improve speed.

    files: A file path or a list of paths
    yield: P4File instance
    """
    if not files:
        return

    files = tolist(files)
    opened = defaultdict(list)
    for r in p4run('opened', '-as', *files):
        opened[r['depotFile']].append({
            'user': r['user'],
            'action': r['action'],
            'change': r['change']
        })

    for payload in p4run('fstat', *files):
        payload['opened_by'] = []
        for o in opened.get(payload['depotFile'], []):
            payload['opened_by'].append(o['user'])
        yield payload

class P4File(object):

    """
    Wrapper class for a Perforce related file path.
    This class is NOT intended for regular Perforce operations
    such as Add, Edit, Revert, Delete, etc. These operations
    should be performed in P4Changelist class. pyp4 is a changelist
    centric Perforce API.
    This class is rather intended to perform mainly locking related
    operations and showing some basic file attributes. 
    """

    def __init__(self, path=None):
        """
        path: Perforce or local filesystem styled file path. If path is None, the intention
        is to use load() method for the payload, which is used by P4Files class.
        """
        self.__path = None
        if path:
            if is_depot_path(path):
                self.__path = path
            else:
                self.__path = os.path.normpath(path)

        # Basic file attributes
        self.__depot_file = None
        self.__client_file = None
        self.__opened_by = []
        self.__locked_by = []
        self.__have = None
        self.__head = None
        self.__head_type = None
        self.__action = None
        self.__unresolved = None
        self.__cl = None

        self.fetch()

    @property
    def value(self):
        """
        Raw path string (could be normalized).
        """
        return self.__path

    @property
    def depot_file(self):
        """
        File path in Perforce depot style.
        e.g. //foo/bar.txt
        """
        return self.__depot_file

    @property
    def client_file(self):
        """
        File path in client local filesystem.
        e.g. C:\foo\bar.txt
        """
        return self.__client_file

    @property
    def locked_by(self):
        """
        A List of user names who have this file locked. It's usually just one.
        """
        return self.__locked_by

    @property
    def opened_by(self):
        """
        A list of user names who have this file checked out.
        """
        return self.__opened_by

    @property
    def have(self):
        """The revision you have in your client"""
        return self.__have

    @property
    def head(self):
        """Head revision in depot"""
        return self.__head

    @property
    def head_type(self):
        """Head revision file type"""
        return self.__head_type

    @property
    def action(self):
        """
        Type of modification being applied to this file.
        """
        return self.__action

    @property
    def cl(self):
        return self.__cl

    def load(self, payload):
        """
        payload: Result yield by file_fetcher().
        """
        self.__depot_file = payload['depotFile']
        self.__client_file = payload['clientFile']
        try:
            self.__have = int(payload.get('haveRev', 0))
        except ValueError:
            self.__have = -1
        try:
            self.__head = int(payload.get('headRev', 0))
        except ValueError:
            self.__head = -1
        if payload.has_key('headType'):
            self.__head_type = payload['headType']
        elif payload.has_key('type'):
            self.__head_type = payload['type']
        self.__action = payload.get('action')
        self.__unresolved = payload.get('unresolved')

        try:
            # Attempt to convert changelist to int.
            self.__cl = int(payload.get('change'))
        except (TypeError, ValueError):
            self.__cl = payload.get('change')

        self.__opened_by = payload.get('opened_by', [])
        if self.is_exclusive_checkout():
            self.__locked_by = payload.get('opened_by', [])

    def fetch(self):
        """
        Updafile_te this P4File class with file_payload_fetcher().
        """
        path = self.__depot_file
        if self.__path:
            path = self.__path
        if path:
            for payload in file_payload_fetcher(path):
                self.load(payload)

    def is_exclusive_checkout(self):
        return '+l' in self.__head_type
    
    def is_locked(self):
        return bool(self.__locked_by)

    def is_locked_by_other(self):
        return self.__locked_by and self.__locked_by != [p4.user]

    def is_locked_by_me(self):
        return self.__locked_by and self.__locked_by == [p4.user]
    
    def is_head(self):
        """
        True if file is sync'ed to head.
        """
        return self.__have and self.__have == self.__head

    def exists_in_depot(self):
        """
        False indicates the file does not yet exist on the server.
        """
        return bool(self.__head)

    def exists_in_client(self):
        """
        True if client file exists on local filesystem
        """
        return os.path.exists(self.__client_file)

    def owner(self, revision=None):
        """
        Revision number starts at 1, not 0.
        If revision is not specified, all owners of this file are returned,
        ordered from the oldest to the newest.

        revision: P4 file revision number
        """
        if self.action == 'add':
            users = [p4.user]
        else:
            users = p4run('filelog', self.__client_file)['user']
        users.reverse()
        if revision is None:
            return users
        return users[revision-1]

    def lock(self):
        """
        Gain exclusive access to this file. Other users cannot check out this file
        any more after it is locked.
        """
        try:
            p4run('lock', self.__client_file)
        except P4Exception as why:
            # Re-arrange exception message to better inform user before locking a file.
            if 'file(s) not opened on this client' in why.value:
                why = 'Please checkout file before locking: {0}'.format(self.__client_file)
            raise P4Exception(why)
        self.fetch()

    def unlock(self):
        """
        Release exclusive access to this file.
        """
        try:
            p4run('unlock', self.__client_file)
        except P4Exception as why:
            # Re-arrange exception message to better inform user before unlocking a file.
            if 'file(s) not opened on this client' in why.value:
                why = 'Please checkout file before unlocking: {0}'.format(self.__client_file)
            raise P4Exception(why)
        self.fetch()

    def sync(self):
        p4sync(self.__client_file)
        self.fetch()

    def revert(self):
        if self.is_opened():
            p4run('revert', self.__client_file)
            self.fetch()

    def is_opened(self):
        """
        Open means checkout in Perforce lingo
        """
        return self.__action is not None

    def is_unresolved(self):
        return bool(self.__unresolved)

    def __str__(self):
        """
        return: A string representation of this changelist.
        """
        _str = []
        _str.append('Exists in Depot: {0}'.format(self.exists_in_depot()))
        _str.append('Depot: {0}'.format(self.__depot_file))
        _str.append('Client: {0}'.format(self.__client_file))
        _str.append('Have: {0}'.format(self.__have))
        _str.append('Head: {0}'.format(self.__head))
        _str.append('Head Type: {0}'.format(self.__head_type))
        _str.append('Action: {0}'.format(self.__action))
        _str.append('Unresolved: {0}'.format(self.is_unresolved()))
        _str.append('Locked by: {0}'.format(self.__locked_by))
        _str.append('Opened by: {0}'.format(self.__opened_by))
        _str.append('')
        return os.linesep.join(_str)

    def dump(self):
        """
        Print the string representation of this changelist.
        """
        print(self)

    def __eq__(self, item):
        """
        Override "==" operator to test if "item" is the same as this P4File.

        item: A file path or a P4File instance.
        return: True if they are the same, otherwise False.
        """
        if isinstance(item, P4File):
            p4f = item
        elif isinstance(item, types.StringTypes):
            p4f = P4File(item)
        else:
            raise TypeError('Expects a file path or a P4File instance. Found {0}.'.format(type(item)))
        return self.__depot_file == p4f.__depot_file

    def __ne__(self, item):
        """
        Override '!=' operator to test if "item" is not the same as this P4File.

        item: A file path or a P4File instance.
        return: True if they are the same, otherwise False.
        """
        return not self.__eq__(item)


