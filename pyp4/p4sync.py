#!/usr/bin/env python

from pyp4.p4command import p4run

class P4Sync(object):

    def __init__(self):
        self.force = None
        self.parallel = None
        self.quiet = None
        self.safety = None
        self.__preview = None
        slef.__preview_summary = None
        self.reset()

    @property
    def preview(self):
        return self.__preview

    @preview.setter
    def preview(self, b):
        self.__preview = bool(b)
        self.__preview_summary = not self.__preview

    @property
    def preview_summary(self):
        return self.__preview_summary

    @preview_summary.setter
    def preview_summary(self, b):
        self.__preview_summary = bool(b)
        self.__preview = not self.__preview_summary

    def reset(self):
        self.force = False
        self.parallel = ''
        self.quiet = True
        self.safety = False

    def __cmd(self, *flags):
        cmd = ['sync']
        if self.force:
            cmd.append('-f')
        if self.quiet:
            cmd.append('-q')
        if self.safety:
            cmd.append('-s')
        if self.preview:
            cmd.append('-n')
        if self.preview_summary:
            cmd.append('-N')
        if self.parallel:
            cmd.append(self.parallel)
        cmd += flags
        return cmd

    def sync(self, path):
        return p4run(self.__cmd(path))

    def flush(self, path):
        return p4run(self.__cmd('-k', path))

    def update(self, path):
        return p4run(self.__cmd('-s', path))

if __name__ == '__main__':
    pass
