#!/usr/bin/env python

from pprint import pprint
from pyp4.p4command import p4run

class _Checkin(object):

    def __init__(self):
        self._rev = None
        self.user = None
        self.type = None
        self.depot_file = None
        self.description = None
        self._file_size = None
        self.time = None
        self.digest = None
        self._changelist = None
        self.action = None
        self.client = None

    @property
    def rev(self):
        return int(self._rev)

    @rev.setter
    def rev(self, r):
        self._rev = int(r)

    @property
    def file_size(self):
        return int(self._file_size)

    @file_size.setter
    def file_size(self, size):
        self._file_size = int(size)

    @property
    def changelist(self):
        return int(self._changelist)

    @changelist.setter
    def changelist(self, cl):
        self._cl = int(cl)

    def __getitem__(self, key):
        if key in self.keys():
            return getattr(self, key)
        raise KeyError('"{0}" does not exist.'.format(key))

    def keys(self):
        return ('rev', 'user', 'type', 'depot_file', 'description', 'file_size',
            'time', 'digest', 'changelist', 'action', 'client')

    def dump(self):
        pprint(dict(self))

class P4History(object):

    def __init__(self, path):
        self.__path = path
        self.__info = {}
        self.get()

    def get(self):
        self.__info = p4run('filelog', self.__path).first()

    def __checkin(self, rev):
        checkin = _Checkin()
        checkin.rev = self.__info['rev{0}'.format(rev)]
        checkin.user = self.__info['user{0}'.format(rev)]
        checkin.type = self.__info['type{0}'.format(rev)]
        checkin.depot_file = self.__info['depotFile']
        checkin.description = self.__info['desc{0}'.format(rev)]
        checkin.file_size = self.__info['fileSize{0}'.format(rev)]
        checkin.time = self.__info['time{0}'.format(rev)]
        checkin.digest = self.__info['digest{0}'.format(rev)]
        checkin.changelist = self.__info['change{0}'.format(rev)]
        checkin.action = self.__info['action{0}'.format(rev)]
        checkin.client = self.__info['client{0}'.format(rev)]
        return checkin

    def __iter__(self):
        counter = 0
        while True:
            try:
                yield self.__checkin(counter)
            except KeyError:
                return
            counter += 1

    def __getitem__(self, rev):
        return self.__checkin(rev)

    def head(self):
        """
        Returns the newest revision
        """
        for c in self:
            return c

    def tail(self):
        """
        Returns the oldest revision
        """
        o = None
        for c in self:
            o = c
        return o

    def dump(self):
        for checkin in self:
            checkin.dump()

    @property
    def depot_file(self):
        return self.__info['depotFile']


if __name__ == '__main__':
    history = P4History('//swagger/active/fdk/tools/maya/scripts/gen_userGroups.py')
    history.tail().dump()
