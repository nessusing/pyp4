import os
import types
from datetime import datetime

from .p4core import p4run, p4, P4Exception, tolist, p4sync, is_depot_path
from .p4file import P4File, file_payload_fetcher


def changelist_payload_fetcher(changes):
    if not changes:
        return

    changes = tolist(changes)

    # Take care of default changelist first.
    try:
        index = changes.index('default')
    except ValueError:
        pass
    else:
        changes.pop(index)
        yield {
            'change': 'default',
            'depotFile': [r['depotFile'] for r in p4run('opened', '-c', 'default') if r.has_key('depotFile')],
            'status': 'pending',
            'user': p4.user
        }

    if not changes:
        return

    shelved = p4run('describe', '-s', '-S', *changes)
    describes = p4run('describe', '-s', *changes)
    
    if len(shelved) != len(describes):
        raise AssertionError('Number of shelved and describes items should be the same. Shelved: {0}; Describes: {1}'.format(len(shelved), len(describes)))

    counter = 0
    for payload in describes:
        payload['shelved_file'] = shelved.at(counter).get('depotFile', [])
        counter += 1
        yield payload

class P4Changelist(object):
    
    """
    Wrapper class for a Perforce changelist.
    pyp4 is changelist centric. File add, edit, delete, revert, etc
    are all performed in a changelist rather than on a file.
    """

    def __init__(self, cl=None):
        """
        cl: Numeric, default or None. None create a new changelist upon initialization.
        """
        
        # Define more attributes if we need to extract from a changelist.
        # Populate it in fetch method.
        self.__desc = 'pyp4 created this changelist.'
        self.__status = None
        self.__depot_files = []
        self.__shelved_files = []
        self.__p4files = []
        self.__owner = None
        # Note that __clno is always a numeric value.
        # Look inside __translate_cl for details.
        self.__clno = self.__translate_cl(cl)
        self.__time = None

        if self.__clno == -2:
            self.new()
        elif self.__clno >= 0:
            self.fetch()

    @property
    def description(self):
        return self.__desc

    @description.setter
    def description(self, desc):
        # Only non default changelist can have description
        if self.__clno > 0:
            change = p4run('change', '-o', self.__clno)
            change['Description'] = desc
            p4.input = change.value
            p4run('change', '-i')
            self.fetch()
        if self.is_default(): # Default changelist
            self.__desc = desc

    @property
    def cl(self):
        """Either a numeric value or default or None"""
        if self.__clno == 0:
            return 'default'
        if self.__clno == -1:
            return 'payload'
        if self.__clno == -2:
            # -2 should never acutally exist inside this class.
            # As soon as -2 is supplied in __init__(cl=-2) or __init__(cl=None), 
            # a new change will be created with a real changelist number assigned
            # to this class.
            raise AssertionError('__clno should never actually reach -2 value.')
        return self.__clno

    @property
    def clno(self):
        """
        Changelist in numberic value.
        """
        return self.__clno

    @property
    def depot_files(self):
        """List of files checked out in this changelist."""
        return self.__depot_files

    @property
    def shelved_files(self):
        """
        List of files shelved in this changelist if this is a pending changelist.
        """
        return self.__shelved_files

    @property
    def p4files(self):
        """
        List of P4File instances.
        """
        return self.__p4files

    @property
    def status(self):
        """ Usually its either pending or submitted."""
        return self.__status

    @property
    def owner(self):
        """The user who create (submitted) this changelist."""
        return self.__owner

    @property
    def time(self):
        """This is the time when this changelist is created."""
        if self.__time:
            return int(self.__time)
        return self.__time

    @staticmethod
    def __translate_cl(cl):
        """
        'default' is translated to 0
        '-1' indicates payload is used
        '-2' indicates new changelist

        cl: Number, None or 'default'
        return: Translated changelist number as an integer
        """
        if isinstance(cl, types.StringTypes):
            if cl == 'default':
                return 0
            elif cl.isdigit():
                return int(cl)
            else:
                raise ValueError('Wrong value for changelist: {0}'.format(cl))
        elif isinstance(cl, types.IntType):
            return cl
        elif cl is None:
            return -2
        else:
            raise TypeError('Wrong type for changelist: {0}'.format(type(cl)))

    def load(self, payload):
        """
        payload: Result yield by file_payload_fetcher().
        """
        self.__clno = self.__translate_cl(payload['change'])
        self.__status = payload.get('status')
        self.__depot_files = payload.get('depotFile', [])
        self.__desc = payload.get('desc')
        self.__owner = payload.get('user')
        self.__time = payload.get('time')
        self.__shelved_files = payload.get('shelved_file', [])
        for payload in file_payload_fetcher(self.__depot_files):
            p4f = P4File()
            p4f.load(payload)
            self.__p4files.append(p4f)

    def fetch(self):
        """
        Update this changelist using payload_fetcher.
        """
        if self.__clno >= 0:
            for pl in changelist_payload_fetcher(self.cl):
                self.load(pl)

    def is_default(self):
        return self.cl == 'default'

    def is_pending(self):
        return self.__status == 'pending'

    def is_submitted(self):
        return self.__status == 'submitted'

    def new(self, bring_files_in_default=False):
        """
        Make a new changelist.
        This is generally used when None is given in the init method.

        bring_files_in_default: If it is set to True, checked out files in default changelist
        will be moved to this new changelist.
        """
        change = p4run('change', '-o')
        change['Description'] = self.__desc
        if not bring_files_in_default:
            change['Files'] = []
        p4.input = change.value
        result = p4run('change', '-i')
        self.__clno = self.__translate_cl(result.first().split()[1])
        self.fetch()
        return result

    def reopen(self, files, cl=None):
        """
        Move checked out files from another changelist to this changelist.

        files: A file path or a list of paths
        cl: Destination changelist. Default is this changelist.
        """
        if not files:
            return

        files = tolist(files)
        if cl is None:
            cl = self.cl
        result = p4run('reopen', '-c', cl, *files)
        self.fetch()
        return result
    
    def edit(self, files, sync_head=True):
        """
        Open files to edit.

        files: A file path or a list of paths
        sync_head: Sync to head revision before edit
        """
        if not files:
            return

        files = tolist(files)

        for f in files:
            p4f = P4File(f)
            # P4 edit does not raise exception if the file is locked.
            # It just silently fails to edit.
            # I want to raise an exception if a file is locked by other users.
            if p4f.is_locked_by_other():
                raise P4Exception('{0} is locked by {1}.'.format(f, p4f.locked_by))

        # Sync before edit
        if sync_head:
            p4sync(files)

        result = p4run('edit', '-c', self.cl, *files)
        self.fetch()
        return result

    def add(self, files):
        """
        Open files to add.

        files: A file path or a list of paths
        """
        if not files:
            return
        files = tolist(files)
        result = p4run('add', '-c', self.cl, *files)
        self.fetch()
        return result

    def checkout(self, files, sync_head=True):
        """
        Open files to edit or add. This is a hybrid method that attempts 
        to edit or add a file to this changelist.

        files: A file path or a list of paths
        """
        if not files:
            return

        for f in tolist(files):                
            try:
                result = self.edit(f, sync_head)
            except P4Exception:
                result = self.add(f)

            # File could be already checked out in other changelist.
            # Move it back to this changelist.
            _result = result.first()
            if "use 'reopen'" in _result or 'already opened for add' in _result:
                self.reopen(f)

        self.fetch()
        return result

    def mark_for_delete(self, files):
        """
        Delete files

        files: A file path or a list of paths
        """
        if not files:
            return

        result = p4run('delete', '-v', '-c', self.cl, *files)
        self.fetch()
        return result

    def revert(self, files):
        """
        Remove files from this changelist.

        files: A file path or a list of paths
        """
        if not files:
            return
        files = tolist(files)
        result = p4run('revert', '-c', self.cl, *files)
        self.fetch()
        return result

    def revert_unchanged(self):
        """
        Only remove unchanged files from this changelist.
        """
        result = p4run('revert', '-a', '-c', self.cl)
        self.fetch()
        return result

    def empty(self):
        """
        Revert checked out files and delete shelved files in this 
        pending changelist
        """
        self.fetch()
        self.revert(self.__depot_files)
        if self.__clno > 0:
            self.delete_shelved(self.__shelved_files)
        self.fetch()    

    def delete(self):
        """
        Remove this changelist. It first reverts and unshelves
        files in this changelist before removing itself.
        
        **IMPORTANT NOTE:
        Note that after deletion, this changelist turns into default
        changelist. This is to give this changelist a post deletion 
        state. Users are NOT advised to continue using this changelist
        after its deletion.
        """
        self.fetch()
        self.revert(self.__depot_files)
        if self.__clno > 0:
            self.delete_shelved(self.__shelved_files)
            result = p4run('change', '-d', self.cl)
            self.__init__('default')
            return result

    def submit(self):
        """
        Check in this changelist.
        """
        # Create a new changelist before submission if it is default.
        if self.is_default():
            self.new(bring_files_in_default=True)
        result = p4run('submit', '-c', self.cl)
        for item in result:
            if item.has_key('submittedChange'):
                self.__clno = self.__translate_cl(item['submittedChange'])
                self.fetch()
                break
        return result

    def delete_shelved(self, files):
        """
        Remove files from shelve in this changelist.

        files: A file path of a list of paths
        """
        if not files:
            return
        files = tolist(files)
        result = p4run('shelve', '-d', '-c', self.cl, *files)
        self.fetch()
        return result

    def shelve(self, files, keep=True):
        """
        Shelve files to this changelist if it is a pending changelist.

        files: A file path or a list of paths
        keep: Leave files in changelist alone otherwise they are removed
        """
        if not files:
            return
        files = tolist(files)
        result = p4run('shelve', '-f', '-c', self.cl, *files)
        if not keep:
            self.revert(files)
        self.fetch()
        return result

    def unshelve(self, files, keep=True, cl=None):
        """
        Unshleve files from this changelist if it is a pending changelist.

        files: A file path or a list of paths
        keep: Leave files in the shelf otherwise they are removed
        """
        if not files:
            return
        files = tolist(files)
        if cl is None:
            cl = self.cl
        result = p4run('unshelve', '-s', self.cl, '-f', '-c', cl, *files)
        if not keep:
            self.delete_shelved(files)
        self.fetch()
        return result

    def __str__(self):
        """
        return: A string representation of this changelist.
        """
        _str = []
        _str.append('Change: {0}'.format(self.cl))
        _str.append('Description: {0}'.format(self.__desc))
        _str.append('Owner: {0}'.format(self.__owner))
        _str.append('Status: {0}'.format(self.__status))
        if self.time:
            _str.append('Date Created: {0}'.format(datetime.fromtimestamp(self.time).strftime('%m/%d/%Y %H:%M:%S')))
        else:
            _str.append('Date Created: None')
        _str.append('Files:')
        for f in self.__depot_files:
            _str.append(' -{0}'.format(f))
        if self.is_pending():
            _str.append('Shelved:')
            for f in self.__shelved_files:
                _str.append(' -{0}'.format(f))
        _str.append('')
        return os.linesep.join(_str)

    def dump(self):
        """
        Print the string representation of this changelist.
        """
        print(self)

    def __contains__(self, item):
        """
        Override "in" operator to test if this changelist contains
        the file.

        item: A file path or a P4File instance
        """
        if isinstance(item, types.StringTypes):
            p4f = P4File(item)
        elif isinstance(item, P4File):
            p4f = item
        else:
            raise TypeError('Expect a string file path or P4File instance. Found: {0}'.format(type(item)))
        return p4f in self.__p4files


