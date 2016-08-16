#!/usr/bin/env python

from pprint import pprint
from pyp4.p4command import p4run

class P4Client(object):

    def __init__(self, name):
        self.__name = name
        self.__info = None
        self.get()

    def get(self):
        self.__info = p4run('client', '-o', self.__name).first()

    def set(self):
        return p4run('client', '-i', stdin=self.__info)

    def update(self):
        return self.set()

    def delete(self, force=False):
        cmd = ['client']
        if force:
            cmd.append('-f')
        cmd.append('-d')
        cmd.append(self.__name)
        return p4run(*cmd)

    def reconcile(self):
        pass

    def dump(self):
        pprint(self.__info)

    def __getitem__(self, name):
        return self.__info[name]

    def __setitem__(self, name, value):
        self.__info[name] = value

    def keys(self):
        return self.__info.keys()

if __name__ == '__main__':
    client = P4Client('LARRYW-3325_swagger_stream')
    client.dump()
