#!/usr/bin/env python

import os
import subprocess

from pprint import pprint
from pyp4.p4command import p4run
from pyp4.p4exception import *
from pyp4.p4user import P4User
from pyp4.p4client import P4Client

class P4File(object):

    def __init__(self, path=None):
        """
        path: Either Perforce path or local filesystem path.
        """
        self.__path = path
        self.__payload = None
        if path:
            self.update()

    def update(self):
        self.__payload = p4run('fstat', self.__path).first()

    @property
    def payload(self):
        return self.__payload

    def set_payload(self, pl):
        self.__payload = pl

    def __getitem__(self, key):
        return self.__payload[key]

    def keys(self):
        return self.__payload.keys()

    @property
    def have_rev(self):
        return int(self.__payload['haveRev'])

    @property
    def head_rev(self):
        return int(self.__payload['headRev'])

    @property
    def depot_file(self):
        return self.__payload['depotFile']

    @property
    def client_file(self):
        return self.__payload['clientFile']

    def dump(self):
        pprint(self.__payload)

    def is_mapped(self):
        return self.__payload.has_key('isMapped')

    def at_head(self):
        return self.have_rev == self.head_rev

    def is_resolved(self):
        return not self.__payload.has_key('unresolved')

    def locked(self):
        """
        Returns None if file is not locked,
        otherwise returns the user and the client the file is locked with.
        """
        for result in p4run('opened', '-a', self.__path):
            if '+l' in result['type'] or '+m' in result['type']:
                user = P4User(result['user'])
                client = P4Client(result['client'])
                return user, client

    def lock(self):
        r = p4run('lock', self.__path)
        self.update()
        return r

    def unlock(self):
        r = p4run('unlock', self.__path)
        self.update()
        return r

    def is_new(self):
        return not bool(self.__payload)

    def is_opened(self):
        return self.__payload.has_key('action')

    def checkout(self, cl):
        if self.is_new():
            return self.add(cl)
        return self.edit(cl)

    def add(self, cl):
        r = p4run('add', '-c', cl, self.__path)
        self.update()
        return r

    def edit(self, cl):
        result = p4run('edit', '-c', cl, self.__path)
        try:
            # file already opened for edit in a different changelist, attempt to
            # reopen it.
            if "use 'reopen'" in result.first()['data']:
                result = self.reopen(cl)
        except (KeyError, TypeError):
            pass
        self.update()
        return result

    def revert(self, quiet=True, only_unchanged=False):
        cmd = ['revert']
        if only_unchanged:
            cmd.append('-a')
        cmd.append(self.__path)
        try:
            r = p4run(*cmd)
            self.update()
            return r
        except P4Exception:
            if not quiet:
                raise

    def delete(self, cl, force=True):
        if force:
            self.revert()
        r = p4run('delete', '-c', cl, self.__path)
        self.update()
        return r

    def reopen(self, cl):
        r = p4run('reopen', '-c', cl, self.__path)
        self.update()
        return r

    def sync(self, rev=None):
        path = self.__path
        if rev is not None:
            path += '#' + rev
        r = p4run('sync', path)
        self.update()
        return r

    def open(self, editor, *flags):
        cmd = [editor]
        cmd += flags
        cmd.append(self.client_file)
        proc = subprocess(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.communicate()

    def rename(self, tofile, cl=None, force=False):
        if not self.is_open():
            raise P4Exception('Please open this file for edit first: {0}'
                .format(self.__path))
        cmd = ['move']
        if cl is not None:
            cmd.append('-c')
            cmd.append(cl)
        if force:
            cmd.append('-f')
        cmd.append(self.__path)
        cmd.append(tofile)
        r = p4run(*cmd)
        self.update()
        return r

    def move(self):
        self.rename()

    def merge(self):
        self.update()

    def resolve(self):
        self.update()

    def tag(self):
        self.update()

    def diff(self):
        pass

def p4files(files):
    p4files = []
    for r in p4run('fstat', *files):
        p4file = P4File()
        p4file.info = r
        p4files.append(p4file)
    return p4files

if __name__ == '__main__':
    p4file = P4File('//swagger/active/fdk/tools/maya/scripts/gen_simplygon/common.py')
    print type(p4file.have_rev)
