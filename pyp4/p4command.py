#!/usr/bin/env python

from subprocess import Popen, PIPE
import marshal
import types
from pprint import pprint
import os

from pyp4.p4exception import *
from pyp4.p4log import p4log

p4 = 'p4' # P4 client executable path

def check_p4(env=None):
    try:
        Popen([p4], stdout=PIPE, stderr=PIPE, env=env)
    except Exception:
        return False
    return True

class P4Result(object):

    def __init__(self, proc, stdin=None):
        self.__proc = proc
        self.__stdin = stdin
        self.__stdout = None
        self.__stderr = None
        self.__data = None
        self.__get()

    @property
    def process(self):
        return self.__proc

    @property
    def returncode(self):
        return self.__proc.returncode

    def poll(self):
        return self.__proce.poll()

    @property
    def stdin(self):
        return self.__stdin

    @property
    def stdout(self):
        return self.__stdout

    @property
    def stderr(self):
        return self.__stderr

    @property
    def data(self):
        return self.__data

    def __get(self):

        self.__stdout, self.__stderr = self.__proc.communicate(input=marshal.dumps(self.__stdin, 0))
        if self.__stderr:
            raise P4Exception('Error: {0}'.format(marshale.loads(self.__stderr)))

        self.__data = []
        if self.__stdout.startswith('{'):
            # Borrowed idea from:
            # http://stackoverflow.com/questions/3249822/python-2-6-4-marshal-load-doesnt-accept-open-file-objects-made-with-subprocess
            result = self.__stdout.split('{')
            for r in result[1:]:
                self.__data.append(marshal.loads('{'+r))
        else:
            # Not everything returned by `p4 -G` is marshallable.
            # e.g. p4 -G set <env>
            self.__data = [self.__stdout]

    def __verify(self):
        if not self.__data:
            # It is possible to have empty result returned.
            return
        if not isinstance(self.__data, types.ListType):
            raise P4Exception('Only ListType is expected. Found: {0}.'
                .format(type(self.__data)))
        if self.__data[0].has_key('code') and self.__data[0]['code'] == 'error':
            error = self.__data[0]['data'].strip()
            # Attempt to categorize different error types.
            if error.endswith('no such file(s).'):
                raise P4NoSuchFileError(error)
            raise P4Exception(self.__data[0]['data'])

    def first(self):
        for item in self:
            return item

    def last(self):
        ret = None
        for item in self:
            ret = item
        return ret

    def __iter__(self):
        for item in self.__data:
            yield item

    def __getitem__(self, index):
        return self.__data[index]

    def __len__(self):
        return len(self.__data)

    def __non_zero__(self):
        return bool(self.__data)

    def dump(self):
        pprint(self.__data)


def p4run(*args, **kwargs):
    """
    Note: Python 2.x does not seem to support named arguments after arbitrary list
    arguments. Both of them needs to be arbitrary at this point.
    Reference: http://stackoverflow.com/questions/5940180/python-default-keyword-arguments-after-variable-length-positional-arguments
    """
    cmd = [p4, '-G'] + [str(arg) for arg in args] # Stringnify before join
    # p4log.cmd(cmd)
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=kwargs.get('env', None))
    return P4Result(proc, stdin=kwargs.get('stdin', None))

if __name__ == '__main__':
    pass
