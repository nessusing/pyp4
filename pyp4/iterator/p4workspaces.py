#!/usr/bin/env python

from pyp4.p4command import p4run
from pyp4.p4user import P4User
from pyp4.p4client import P4Client

class P4Workspaces(object):

    def __init__(self):
        self.owner = None
        self.name_filter = None
        self.limit = None
        self.case_sensitive = None
        self.stream = None

        self.reset()

    def reset(self):
        self.owner = P4User().name
        self.name_filter = None
        self.limit = 50
        self.case_sensitive = True
        self.stream = None

    def __iter__(self):
        cmd = ['workspaces']
        if self.owner:
            cmd.append('-u')
            cmd.append(self.owner)
        if self.name_filter:
            if self.case_sensitive:
                cmd.append('-e')
            else:
                cmd.append('-E')
            cmd.append(self.name_filter)
        if self.limit:
            cmd.append('-m')
            cmd.append(self.limit)
        if self.stream:
            cmd.append('-S')
            cmd.append(self.stream)
        for r in p4run(*cmd):
            yield P4Client(r['client'])

    def dump(self):
        for client in self:
            client.dump()

if __name__ == '__main__':
    for ws in P4Workspaces():
        ws.dump()
