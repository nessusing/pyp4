
from _winreg import *
import maya.cmds as cmds

def get_perforce_registry(key):
    aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
    aKey = OpenKey(aReg, r"Software\perforce\environment", 0, KEY_ALL_ACCESS)
    return QueryValueEx(aKey, key)[0]


def set_perforce_clientspec(clientspec, port, user):
    keyVal = r'Software\perforce\environment'
    key = CreateKey(HKEY_CURRENT_USER, keyVal)
    SetValueEx(key, "P4CLIENT", 0, REG_SZ, clientspec)
    SetValueEx(key, "P4PORT", 0, REG_SZ, port)
    SetValueEx(key, "P4USER", 0, REG_SZ, user)
    CloseKey(key)

def check_perforce_clientspec(contains_string):
    clientspec = get_perforce_registry("P4CLIENT")
    port = get_perforce_registry("P4PORT")
    if contains_string in clientspec:
        return True
    elif len(clientspec)<=0:
        return True
    else:
        return False

def make_perforce_clientspec_window():

    if cmds.window('p4_clientspec_window', exists=True):
        cmds.deleteUI('p4_clientspec_window')
    old_clientspec = get_perforce_registry("P4CLIENT")
    old_port = get_perforce_registry("P4PORT")
    old_user = get_perforce_registry("P4USER")

    cmds.window(['p4_clientspec_window'], title='P4', widthHeight=(200,400), sizeable=False)
    cmds.frameLayout( label = "P4 Clientspec", borderStyle = "etchedIn")
    cmds.gridLayout ( numberOfColumns = 1, cellWidthHeight =(200, 30))

    cmds.text("Looks like your P4 credentials are missing or incorrect in Windows Registry...:( \r", wordWrap=True)
    cmds.text('  Please input new credentials:' , wordWrap=True)
    cmds.text("ClientSpec:")
    cmds.textField('clientspec')
    cmds.textField('clientspec', edit=True, text=old_clientspec)
    cmds.text("Port:")
    cmds.textField('port')
    cmds.textField('port', edit=True, text=old_port)
    cmds.text("User")
    cmds.textField('user')
    cmds.textField('user', edit=True, text=old_user)
    cmds.button(l='Change Clientspec', c=lambda *args:set_clientspec())
    cmds.setParent('..')
    cmds.showWindow('p4_clientspec_window')

def set_clientspec():
    old_clientspec = get_perforce_registry("P4CLIENT")
    old_port = get_perforce_registry("P4PORT")
    old_user = get_perforce_registry("P4USER")
    new_clientspec = cmds.textField('clientspec', text=True, query = True)
    new_port = cmds.textField('port', text=True, query = True)
    new_user = cmds.textField('user', text=True, query = True)
    set_perforce_clientspec(new_clientspec,new_port,new_user)
    cmds.confirmDialog(title='',message="Thanks!!!", button=['OK'],defaultButton='OK')
    cmds.deleteUI('p4_clientspec_window')


def check_p4_registry():
    badStream = check_perforce_clientspec("swagger")
    if badStream:
        return False
    else:
        return True