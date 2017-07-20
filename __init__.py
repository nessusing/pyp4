
from P4 import P4, P4Exception
from .p4core import *
from .p4changelist import P4Changelist
from .p4pending import P4Pending
from .p4file import P4File
from .p4stream import P4Stream
from .p4factory import *

"""
A simple wrapper for Python P4 API.

p4factory.py contains most of the top level api functions. 
Please check this file for a complete list of public methods.

Example:
-------------------------------------------------------------------

import pyp4

# Make a list of files
files = []
files.append('c:/foo/bar1.txt')
files.append('c:/foo/bar2.txt')
files.append('//foo/bar3.txt') # File path can be either client or Perforce sytle

# To create a new changelist with above files
# It returns a P4Changelist object
change = pyp4.checkout(files, 'This is my description.')

# You can also checkout a files inside a directory recursively (files in sub-folders also gets checked out)
change = pyp4.checkout('c:/myproject/')

# To check out files with specific file extensions inside a directory
# This will check out any files with .png and .mb inside c:/myproject and its sub-folders
change = pyp4.checkout('c:/myproject/', extionsion=['.png', '.mb'])

# To create an empty changelist
change = P4Changelist()
print change.cl # Displays the newly created changelist number

# To "guess" a changelist based on its description
# The description provided does not need to be a full description. As long as its partially matched.
# Note: Only the first changelist that matches will be returned.
pyp4.find_changelist_by_desc("foobar")

# To "guess" a changelist by a file.
pyp4.find_changelist_by_file('c:/foobar.txt')

# To figure out the locking state of a file
p4f = pyp4.P4File('c:/foobar.txt')
p4f.is_locked() # Is the file locked
p4f.is_locked_by_me()
p4f.is_locked_by_other()

# List of users who have this file locked. By definition there should be only 1 user who can
# locked a given file. A list is returned to be compatible with per4ce module.
p4f.locked_by 

"""

