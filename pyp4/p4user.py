#!/usr/bin/env python

from pprint import pprint
from pyp4.p4command import p4run
from pyp4.p4exception import *
from pyp4.p4server import P4Server
from pyp4.p4client import P4Client


class P4User(object):

    def __init__(self, user=None):
        self.__user = user or P4Server.p4user
        self.__info = p4run('users', self.__user).first()

    @property
    def name(self):
        return self.__user

    def __str__(self):
        return self.name

    def login(self, host=None):
        cmd = ['login']
        if host:
            cmd.append('-h')
            cmd.append(host)
        cmd.append(self.__user)
        return p4run(*cmd)

    def logout(self):
        return p4run('logout')

    def change_password(self, pw, oldpw=None):
        cmd = ['passwd']
        if oldpw is not None:
            cmd.append('-O')
            cmd.append('oldpw')
        cmd.append('-P')
        cmd.append(pw)
        return p4run(*cmd)

    def groups(self):
        pass

    def opened(self):
        return p4run('opened', '-u', self.__user)

    def clients(self):
        return [item['client'] for item in p4run('clients', '-u', self.__user)]

    def current_client(self):
        return P4Server.clientName

    def p4clients(self):
        return [P4Client(client) for client in self.clients()]

    def current_p4client(self):
        return P4Client(self.current_client())

    @property
    def email(self):
        return self.__info['Email']

    @property
    def full_name(self):
        return self.__info['FullName']

    def dump(self):
        d = self.__info.copy()
        d['clients'] = self.clients()
        d['current_client'] = self.current_client()
        pprint(self.__info)


if __name__ == '__main__':
    p4user = P4User()
    print p4user.clients()
