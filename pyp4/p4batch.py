#!/usr/bin/env python

from pyp4.p4command import p4run
from pyp4.p4file import P4File

def make_p4files(files):
    p4files = []
    for r in p4run('fstat', *files):
        p4file = P4File()
        p4file.set_payload(r)
        p4files.append(p4file)
    return p4files

def make_p4changelist(changelists):
    pass
