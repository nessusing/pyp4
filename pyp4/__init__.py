#!/usr/bin/env python

DEBUG = False

from pyp4.p4command import P4Result, p4run


from pyp4.p4branch import P4Branch
from pyp4.p4changelist import P4Changelist
from pyp4.p4client import P4Client
from pyp4.p4exception import *
from pyp4.p4file import P4File
from pyp4.p4path import P4Path
from pyp4.p4label import P4Label
from pyp4.p4log import p4log
from pyp4.p4server import P4Server
from pyp4.p4stream import P4Stream
from pyp4.p4sync import P4Sync
from pyp4.p4user import P4User

from pyp4.iterator.p4branches import P4Branches
from pyp4.iterator.p4browser import P4Browser
from pyp4.iterator.p4history import P4History
from pyp4.iterator.p4labels import P4Labels
from pyp4.iterator.p4pending import P4Pending
from pyp4.iterator.p4streams import P4Streams
from pyp4.iterator.p4submitted import P4Submitted
from pyp4.iterator.p4workspaces import P4Workspaces

'''
Things left to do:
- stream and streams classes
- logging (done)
- testing
'''
