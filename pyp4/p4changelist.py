#!/usr/bin/env python

import types
from pprint import pprint
from pyp4.p4exception import *
from pyp4.p4file import P4File, p4files
from pyp4.p4command import p4run
from pyp4.p4server import P4Server
from pyp4.p4shelf import P4Shelf

class P4Changelist(object):

    def __init__(self, cl=None):
        self.__cl = cl
        self.__payload = None
        self.__shelf = None
        self.__p4files = []
        self.__files = []
        if cl is not None:
            P4Changelist.validate(cl)
            self.update()

    @staticmethod
    def validate(cl):
        try:
            int(cl)
        except Exception:
            is_passed = cl == 'default'
        else:
            is_passed = True

        if not is_passed:
            raise P4Exception('Changelist can only be integer, "default" or None. "{0}" given.'.format(cl))

    def is_default(self):
        return self.__cl == 'default'

    def update(self):
        if self.is_default():
            self.__payload = p4run('opened', '-c', self.__cl)
            self.__files = [item['depotFile'] for item in self.__payload]
        else:
            self.__payload = p4run('describe', self.__cl).first()
            if self.__shelf is None and self.status == 'pending':
                self.__shelf = P4Shelf(self)
            self.__files = [value for key, value in self.__payload.iteritems() if key.startswith('depotFile')]
        self.__p4files = p4files(self.__files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        try:
            return self.__p4files[index]
        except IndexError:
            raise IndexError('Unable to find file at index: {0} in changelist: {1}'.format(index, self.__cl))

    def __iter__(self):
        for p4file in self.__p4files:
            yield p4file

    @property
    def files(self):
        """
        Returns a list of depot file path belong to this changelist.
        """
        return self.__files

    @property
    def payload(self):
        return self.__payload

    @property
    def description(self):
        if self.is_default():
            return
        try:
            return self.__payload['desc']
        except (KeyError, TypeError):
            return

    @description.setter
    def description(self, d):
        if self.is_default():
            p4files = [p4file for p4file in self]
            self.new(description=d)
            for p4file in p4files:
                p4file.reopen(self.__cl)
        else:
            p4run('change', '-i', stdin={
                'Description': str(d),
                'Change': str(self.__cl)
            })
        self.update()

    @property
    def changelist(self):
        return self.__cl

    @property
    def status(self):
        if self.is_default():
            return
        return self.__payload['status']

    def __attach_file(self, path, operator, **kwargs):
        if self.status != 'pending':
            raise P4Exception('Only pending changelist can be modified.')
        getattr(P4File(path), operator)(self.changelist, **kwargs)

    def __attach_files(self, paths, operator, **kwargs):
        for path in paths:
            self.__attach_file(path, operator, **kwargs)

    def __attach(self, thing, operator, **kwargs):
        if isinstance(thing, (types.ListType, types.TupleType)):
            self.__attach_files(thing, operator, **kwargs)
        else:
            self.__attach_file(thing, operator, **kwargs)

    def checkout(self, thing):
        self.__attach(thing, 'checkout')
        self.update()

    def add(self, thing):
        self.__attach(thing, 'add')
        self.update()

    def edit(self, thing):
        self.__attach(thing, 'edit')
        self.update()

    def revert(self, thing, quiet=True, only_unchanged=False):
        self.__attach(thing, 'revert', quiet=quiet, only_unchagned=only_unchanged)
        self.update()

    def new(self, description='pyp4 created this changelist.'):
        result = p4run('change', '-i', stdin={
            'Description': str(description),
            'User': P4Server.p4user,
            'Change': 'new'
        })
        # Update changelist from the result.
        self.__cl = result.first()['data'].split()[1]
        # Update changelist info
        self.update()
        return result

    def delete(self, force=True):
        if force:
            for p4file in self:
                p4file.revert()
            if self.__shelf:
                self.__shelf.delete()
        result = p4run('change', '-d', self.__cl)
        self.__payload = None
        return result

    @property
    def shelf(self):
        return self.__shelf

    def submit(self):
        if not len(self):
            raise P4Exception('Cannot submit empty changelist.')
        if self.__shelf and len(self.__shelf):
            raise P4Exception('Shelved files needs to be emptied before submission.')
        if not self.description:
            raise P4Exception('Please write a description first.')

        unresolved = []
        for p4file in self:
            if not p4file.is_resolved():
                unresolved.append(p4file)
        if unresolved:
            raise P4Exception('Please resolve following files before submission:\n{0}'
                .format([p4file.client_file for p4file in unresolved]))
        result = p4run('submit', '-c', self.__cl)
        self.__cl = result[-1]['submittedChange']
        self.update()
        return result

    def __str__(self):
        return str(self.changelist)

    def __cmp__(self, cl):
        """
        'Default' is treated as 0, which is the lowest changelist.
        """
        P4Changelist.validate(cl)

        if isinstance(cl, P4Changelist):
            cl = cl.changelist

        # Treating default cl as 0
        if cl == 'default':
            cl = 0
        cl = int(cl)

        this_cl = self.__cl
        if this_cl == 'default':
            this_cl = 0
        this_cl = int(this_cl)

        if this_cl < cl:
            return -1
        elif this_cl == cl:
            return 0
        else:
            return 1

    def dump(self):
        print 'File(s):'
        for p4file in self:
            p4file.dump()
        if self.shelf:
            print 'Shelved:'
            for p4file in self.shelf:
                p4file.dump()

if __name__ == '__main__':
    # cl = P4Changelist()
    # cl.new('foobar')
    # cl.checkout('/Users/nessus/Perforce/MacBookPro/projects/pyp4/p4label.py')
    cl = P4Changelist(15)
    print cl.files
    print cl.shelf.files
    # cl.description = 'Update changelist after submission.'
    # r = cl.submit()
    # print cl.changelist
    # print cl.files
