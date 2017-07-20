from .p4core import p4, p4run, tolist, P4Exception
from .p4changelist import P4Changelist

class P4Stream(object):

    def __init__(self, stream=None):
        if stream is None:
            self.__stream = p4run('stream', '-o').first()
        else:
            self.__stream = p4run('stream', '-o', stream).first()

    @property
    def name(self):
        return self.__stream['Name']

    @property
    def stream(self):
        return self.__stream['Stream']

    @property
    def parent(self):
        return self.__stream['Parent']

    @property
    def baseparent(self):
        return self.__stream['baseParent']

    @property
    def type(self):
        return self.__stream['Type']

    @property
    def description(self):
        return self.__stream['Description']

    @property
    def owner(self):
        return self.__stream['Owner']

    @property
    def paths(self):
        try:
            return self.__stream['Paths']
        except KeyError:
            return

    @property
    def ignored(self):
        try:
            return self.__stream['Ignored']
        except KeyError:
            return

    @property
    def access(self):
        return self.__stream['Access']

    def merge(self, changelist, path):
        """
        changelist: A P4Changelist object or changelist number
        path: A Perforce file path
        """
        cl = changelist
        if isinstance(changelist, P4Changelist):
            cl = changelist.clno    
        return p4run('merge', '-c', cl, '-S', self.stream, '-r', path)
