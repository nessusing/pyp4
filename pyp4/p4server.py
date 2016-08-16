#!/usr/bin/env python

import os
from pprint import pprint
from pyp4.p4command import p4run, p4
from pyp4.p4exception import P4Exception

class _P4Server(object):

    def __init__(self):
        self.__info = p4run('info').first()

    def __getitem__(self, name):
        return self.__info[name]

    def set(self, env, value=None):
        if value is None:
            value = ''
        return p4run('set', '{0}={1}'.format(env, value))

    def get(self, env=None):
        cmd = ['set']
        if env is not None:
            cmd.append(env)
        d = {}
        for line in p4run(*cmd).first().strip().split(os.linesep):
            t = line.strip().split('=')
            if len(t) != 2:
                raise P4Exception('Bad line to parse: {0}'.format(line))
            d[t[0]] = t[1].split()[0]
        return d

    @property
    def p4port(self):
        return self.get('P4PORT')['P4PORT']

    @p4port.setter
    def p4port(self, port):
        self.set('P4PORT', value=port)

    @property
    def p4user(self):
        return self.get('P4USER')['P4USER']

    @p4user.setter
    def p4user(self, user):
        self.set('P4USER', value=user)

    def list(self):
        return self.get()

    def dump(self):
        pprint(self.__info)


# Import this global variable for server access. Treat it as singleton.
P4Server = _P4Server()

if __name__ == '__main__':
    P4Server.dump()
    print P4Server.p4port
