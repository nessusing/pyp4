#!/usr/bin/env python

from pprint import pprint
from pyp4.p4command import p4run
from pyp4.p4file import P4File

class P4Files(object):

    def __init__(self, path, recursive=False):
        self.__path = path
        self.__recursive = recursive

    def __iter__(self):
        cmd = ['files']
        path = self.__path
        if self.__recursive:
            path += '/...'
        else:
            path += '/*'
        for r in p4run('files', path):
            yield P4File(r['depotFile'])

    def dump(self):
        for p4file in self:
            p4file.dump()

class P4Dir(object):

    def __init__(self, r):
        self.__r = r
        self.__where = p4run('where', self.r['dir']).first()

    def __getattr__(self, attr):
        return self.__r[attr]

    def __getitem__(self, key):
        return self.__r[key]

    @property
    def client_file(self):
        return self.__where['clientFile']

    @property
    def depot_file(self):
        return self.__where['depotFile']

    def dump(self):
        pprint(self.__r)

class P4Dirs(object):

    def __init__(self, path):
        self.__path = path

    def __iter__(self):
        for r in p4run('dirs', self.__path+'/*'):
            yield P4Dir(r)

    def dump(self):
        for p4dir in self:
            p4dir.dump()

class P4Browser(object):

    @staticmethod
    def clean_path(path):
        while True:
            if path.endswith('/'):
                path = path[:-1]
            else:
                return path

    @staticmethod
    def browse(path):
        path = P4Browser.clean_path(path)
        return P4Dirs(path), P4Files(path)

if __name__ == '__main__':
    # dirs, files = P4Browser.browse('//swagger/active/fdk/tools/maya/scripts/gen_simplygon')
    # for d in dirs:
    #     print d.dir
    # files.dump()

    p4run('where', '//swagger/active/fdk/tools/maya/scripts/gen_simplygon/ui').dump()
