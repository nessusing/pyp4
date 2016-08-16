#!/usr/bin/env python

import os

class _FileName(object):

    def __init__(self):
        self.__name = ''

    def __a(self, name):
        self.__name = name
    name = property(fset=__a)

    def __b(self, name):
        self.__name = '*{0}*'.format(name)
    has = property(fset=__b)
    contains = property(fset=__b)

    def __c(self, name):
        self.__name = '{0}*'.format(name)
    startswith = property(fset=__c)

    def __d(self, name):
        self.__name = '*{0}'.format(name)
    endswith = property(fset=__d)

    def __str__(self):
        return self.__name

class _Range(object):

    def __init__(self):
        self.type = 'changelist'
        self.__start = None
        self.__end = None

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, value):
        self.__start = value

    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, value):
        self.__end = value

    def __str__(self):
        pass


class P4Path(object):

    def __init__(self, base, recursive=True):
        self.__base = base
        self.__recursive = False
        self.__filename = _FileName()
        self.__range = _Range()

    def __str__(self):
        return self.path

    @property
    def path(self):
        return self.join(self.head, self.filename, self.range)

    @staticmethod
    def clean(path):
        while True:
            if path.endswith('/'):
                path = path[:-1]
            else:
                return path

    @staticmethod
    def join(*paths):
        if not paths:
            return
        if paths[0].startswith('//'):
            return '/'.join([P4Path.clean(path for path in paths)])
        else:
            return os.path.join(*paths)

    @property
    def head(self):
        if self.__recursive:
            return self.join(self.__base, '...')
        return self.join(self.__base, '*')

    @property
    def filename(self):
        return self.__filename

    @property
    def range(self):
        return self.__range

    def __str__(self):
        pass

if __name__ == '__main__':
    fn = _FileName()
    fn.startswith = 'haha'
    print fn
