#!/usr/bin/env python

from pyp4.p4command import p4run
from pyp4.p4changelist import P4Changelist
from pyp4.p4user import P4User


class P4Pending(object):

    def __init__(self, p4user=None):
        self.__p4user = p4user or P4User()
        self.__p4changes = {}

    def __iter__(self):
        yield P4Changelist(cl='default')
        for item in p4run('changes', '-u', self.__p4user.name, '-s', 'pending'):
            yield P4Changelist(cl=item['change'])

    def __getitem__(self, cl):
        for p4cl in self:
            if p4cl.changelist == str(cl):
                return p4cl

    def dump(self):
        for p4change in self:
            p4change.dump()

if __name__ == '__main__':
    # import win32file
    # win32file._setmaxstdio(2048)
    pending = P4Pending()
    for change in pending:
        print change
    # print pending['default']
