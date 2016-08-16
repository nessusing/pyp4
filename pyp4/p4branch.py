#!/usr/bin/env python

from pprint import pprint
from pyp4.p4command import p4run

class P4Branch(object):

    def __init__(self, name):
        self.__name = name
        self.__info = {}
        self.get()

    def get(self):
        self.__info = p4run('branch', '-o', self.__name).first()

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def keys(self):
        return self.__info.keys()

    def set(self):
        return p4run('branch', 'i', stdin=self.__info)

    def update(self):
        return self.set()

    def delete(self):
        return p4run('branch', '-d', self.__name)

    def dump(self):
        pprint(self.__info)
