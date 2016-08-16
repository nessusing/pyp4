#!/usr/bin/env python

from pyp4.p4user import P4User
from pyp4.p4command import p4run
from pyp4.p4changelist import P4Changelist

class P4Submitted(object):

    def __init__(self):
        self.owner = None
        self.client = None
        self.limit = None
        self.status = None
        self.path = None

        self.reset()

    def reset(self):
        user = P4User()
        self.owner = user.name
        self.client = user.current_client()
        self.limit = 50
        self.status = None
        self.path = None

    def __iter__(self):
        cmd = ['changelists']
        if self.owner:
            cmd.append('-u')
            cmd.append(self.owner)
        if self.client:
            cmd.append('-c')
            cmd.append(self.client)
        if self.limit:
            cmd.append('-m')
            cmd.append(self.limit)
        if self.status:
            cmd.append('-s')
            cmd.append(self.status)
        if self.path:
            cmd.append(self.path)
        for r in p4run(*cmd):
            yield P4Changelist(cl=r['change'])

    def dump(self):
        for p4change in self:
            p4change.dump()

if __name__ == '__main__':
    sub = P4Submitted()
    for r in sub:
        print r
