files = [r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_ArrayGetPairing.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_AttachHanrdToWeaponSup.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_AttachWeaponToJoint.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_AutoRigChar.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_AutoRigFace.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_AutoRigProp.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeControlRig.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeToIPISkeleton.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeToOLrDSkeleton.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeToSkeleton.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeToSkeletonWOBakingConst.mel',
r'd:\cv\shift\tools\maya\scripts\cv_character_kits\MEL\tc_BakeToSkeleton_OCTANE.mel']

import pymel.core
import pyp4
for f in files:
    pyp4.checkout(f, cl='default')