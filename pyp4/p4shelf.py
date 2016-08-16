#!/usr/bin/env python

from pyp4.p4file import P4File, p4files
from pyp4.p4command import p4run

class P4Shelf(object):

    def __init__(self, p4cl):
        self.__p4cl = p4cl
        self.__payload = None
        self.__files = []
        self.__p4files = []
        if self.__p4cl.status != 'pending':
            raise P4Exception('Non-pending changelist: {0} does not have shelves.'.format(self.__p4cl))
        if self.__p4cl.is_default():
            raise P4Exception('Default changelist cannot have shelved files.')
        self.update()

    def update(self):
        self.__payload = p4run('describe', '-S', '-s', self.__p4cl).first()
        self.__files = [value for key, value in self.__payload.iteritems() if key.startswith('depotFile')]
        self.__p4files = p4files(self.__files)

    def __len__(self):
        return len(self.__files)

    def __getitem__(self, index):
        try:
            return self.__p4files[index]
        except IndexError:
            raise IndexError('Unable to find shelved file at index: {0} in changelist: {1}.'.format(index, self.__p4cl))

    def __iter__(self):
        for p4file in self.__p4files:
            yield p4file

    @property
    def files(self):
        return self.__files

    @property
    def payload(self):
        return self.__payload

    def delete(self, thing):
        result = p4run('shelve', '-d', '-c', self.__p4cl.changelist, *thing)
        self.update()
        return result

    def shelve(self, thing, keep=True):
        result = p4run('shelve', '-f', '-c', self.__cl, *thing)
        if not keep:
            self.__p4cl.revert(thing)
        self.update()
        self.__p4cl.update()
        return result

    def unshelve(self, thing, keep=True):
        """
        thing: A single file path or a list of file paths. None defaults to all
                files.
        """
        result = p4run('unshelve', '-s', self.__p4cl, '-f', '-c', cl, *thing)
        if not keep:
            self.delete(thing=thing)
        self.update()
        self.__p4cl.update()
        return result
