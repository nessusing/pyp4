#!/usr/bin/env python

class P4Exception(Exception):
    pass

class P4NoSuchFileError(P4Exception):
    pass
