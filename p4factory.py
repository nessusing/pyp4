import os
from contextlib import contextmanager

from .p4core import tolist, is_depot_path, touch, p4, p4run
from .p4changelist import P4Changelist, changelist_payload_fetcher
from .p4pending import P4Pending
from .p4file import P4File, file_payload_fetcher


def get_changelist(cl):
    """
    Find the changelist with cl.

    cl: Changelist list number or 'default'. It cannot be None.
    return: P4Changelist object.
    """
    if cl is None:
        raise TypeError('Changelist number cannot be None.')
    return P4Changelist(cl)

def _has_ext(path, extensions):
    """
    path: File path
    extensions: A single file extension (e.g. '.exe') or a list of extensions
    return: True if path's extension belongs to extensions
    """
    _, ext = os.path.splitext(path)
    return ext in tolist(extensions)

def checkout(paths, description=None, cl='new', extensions=None, delete=False):
    """
    Edit or add files in paths recusively.
    Be mindful that this function walks all paths including their subfolders.
    It could get very lengthy if paths are deep!

    Use extensions to filter files for checkout.

    paths: A file path or a list of paths
    cl: Changelist number. Or create a new changelist.
    extensions: A single file extension or a list of extensions
    delete: Mark the files for delete instead of add or edit.
    return: P4Changelist object
    """
    files = set()
    for path in tolist(paths):
        # Ignore depot file path
        # We do not want to use os.path.exists() check this as it will 
        # think this is a network path, try to access it until timeout.
        if is_depot_path(path):
            files.add(path)
            continue
        path = os.path.normpath(path)
        if os.path.isfile(path):
            if extensions is None or _has_ext(path, extensions):
                files.add(path)
        elif os.path.isdir(path):
            for root, _, _files in os.walk(path):
                for f in _files:
                    if extensions is None or _has_ext(path, extensions):
                        files.add(os.path.join(root, f))
        else:
            # This is a special case
            # file is a local filesystem path, but it does not yet exist.
            # This should be supported because for instance, the very
            # first time we ever export something, it does not yet exist.
            touch(path) # Create the dummy file locally for checkout.
            files.add(path)

    if not files:
        raise ValueError('Cannot find any file path in {0}'.format(paths))

    if cl == 'new': cl = None
    change = P4Changelist(cl)
    if delete:
        change.mark_for_delete(files)
    else:
        change.checkout(files)
    if description is not None:
        change.description = description
    return change

def find_changelist_by_desc(partial_desc, fallback_cl=None):
    """
    Find the first changelist which has the description matches the partial description. 

    partial_desc: Part of a description in a changelist
    fallback_cl: Specify which changelist to use if it cannot find. 'default', 'new' and None are supported.
    return: A P4Changelist object or None
    """
    for change in P4Pending():
        if change.description and partial_desc.strip() in change.description.strip():
            return change
    if fallback_cl == 'new':
        return P4Changelist()
    elif fallback_cl == 'default':
        return P4Changelist('default')

def find_cl_by_desc(partial_desc, fallback_cl=None):
    """
    Find the first changelist number which has the description matches the partial description. 

    partial_desc: Part of a description in a changelist
    fallback_cl: Specify which changelist to use if it cannot find. 'default', 'new' and None are supported.
    return: A changelist number or None
    """
    change = find_changelist_by_desc(partial_desc, fallback_cl)
    if change:
        return change.cl

def find_changelist_by_file(path, fallback_cl=None):
    """
    Find the first changelist which has the file checked out in it.

    path: A file path
    fallback_cl: Specify which changelist to use if it cannot find. 'default', 'new' and None are supported.
    return A P4Changelist object or None
    """
    for change in P4Pending():
        if path in change:
            return change
    if fallback_cl == 'new':
        return P4Changelist()
    elif fallback_cl == 'default':
        return P4Changelist('default')

def find_cl_by_file(path, fallback_cl=None):
    """
    Find the first changelist number which has the file checked out in it.

    path: A file path
    fallback_cl: Specify which changelist to use if it cannot find. 'default', 'new' and None are supported.
    return: A changelist number or None
    """
    change = find_changelist_by_file(path, fallback_cl)
    if change:
        return change.cl

def get_pending_changelists(user=p4.user, workspace=p4.client):
    """
    Make a list of pending changelist.

    user: Perforce user name
    workspace: Perfroce clientspec
    return: A list of pending P4Changelist objects
    """
    return [change for change in P4Pending(user, workspace)]

def make_changelist(desc, use_exist=True):
    """
    Create a changelist object.

    desc: Changelist description
    use_exist: Find existing pending changelist with the same description if such exists, otherwise create a new changelist
    return: A changelist object
    """
    if use_exist:
        change = find_changelist_by_desc(desc, fallback_cl='new')
    else:
        change = P4Changelist()
    change.description = desc
    return change

def where(path, client=None):
    """
    path: A file path
    client: Perforce client spec
    return: A dictionary contains different format of the path
    """
    if client is None:
        client = p4.client
    current = p4.client
    p4.client = client
    w = p4run('where', path)
    p4.client = current
    return w.first()

@contextmanager
def changeclient(name):
    current = p4.client
    try:
        p4.client = name
        yield p4
    finally:
        p4.client = current

def p4files(files):
    for payload in file_payload_fetcher(files):
        p4f = P4File()
        p4f.load(payload)
        yield p4f

def p4changelists(changes):
    for payload in changelist_payload_fetcher(changes):
        p4c = P4Changelist()
        p4c.load(payload)
        yield p4c
