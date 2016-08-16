#!/usr/bin/env python

from pyp4.p4command import p4run
from pyp4.p4user import P4User

class P4Labels(object):

    def __init__(self):
        self.owner = None
        self.name_filter = None
        self.case_sensitive = None
        self.limit = None
        self.path = None

    def reset(self):
        self.owner = P4User().name
        self.name_filter = None
        self.case_sensitive = False
        self.limit = 50
        self.path = None

    def __iter__(self):
        cmd = ['labels']
        if self.owner:
            cmd.append('-u')
            cmd.append(self.owner)
        if self.name_filer:
            if self.case_sensitive:
                cmd.append('-e')
            else:
                cmd.append('-E')
            cmd.append(self.name_filter)
        if self.limit:
            cmd.append('-m')
            cmd.append(self.limit)
        if self.path:
            cmd.append(self.path)
        for r in p4run(*cmd):
            yield P4Label(r['label'])
