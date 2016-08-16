#!/usr/bin/env python

from pyp4.p4command import p4run
from pyp4.p4user import P4User
from pyp4.p4branch import P4Branch

class P4Branches(object):

    def __init__(self):
        self.owner = None
        self.name_filter = None
        self.limit = None
        self.case_sensitive = None

    def reset(self):
        self.owner = P4User().name
        self.name_filter = None
        self.limit = 50
        self.case_sensitive = False

    def __iter__(self):
        cmd = ['branches']
        if self.owner:
            cmd.append('-u')
            cmd.append(self.owner)
        if self.name_filter:
            if self.case_sensitive:
                cmd.append('-e')
            else:
                cmd.append('-E')
            cmd.append(name_filter)
        if self.limit:
            cmd.append('-m')
            cmd.append(self.limit)
        for r in p4run(*cmd):
            yield P4Branch(r['branch'])

if __name__ == '__main__':
    branches = P4Branches()
    for r in branches:
        print r
