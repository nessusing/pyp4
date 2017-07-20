import unittest
import types
import pyp4

class TestP4Changelist(unittest.TestCase):

    desc = 'pypy unittest'

    test_files = [
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/Uber Buddies - Instructions.txt',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/__init__.py',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/launch_uberbuddies.py',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/objects.py',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/ub_qt.py',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/ub_shelfs.py',
        '//shift/active/tools/maya/scripts/standalone/uberbuddies/ub_uber_tool.py'
    ]

    test_newfiles = [

    ]

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Delete testing changelists
        I use the same description as identifier for detection.
        """
        for change in pyp4.get_pending_changelists():
            if change.is_default():
                continue
            if change.description.strip() == cls.desc:
                change.delete()

    def test(self):
        change = pyp4.P4Changelist()
        change.description = self.desc
        self.assertIsInstance(change.cl, types.IntType)
        self.assertEqual(len(change.depot_files), 0)
        self.assertEqual(len(change.shelved_files), 0)
        self.assertIsNotNone(change.description)
        self.assertEqual(change.description.strip(), self.desc)
        change.checkout(self.test_files[0])
        self.assertEqual(len(change.depot_files), 1)
        change.checkout(self.test_files[1:3])
        self.assertEqual(len(change.depot_files), 3)
        change.checkout(self.test_files)
        self.assertEqual(len(change.depot_files), len(self.test_files))
        change.revert_unchanged()
        self.assertEqual(len(change.depot_files), 0)
        

    

if __name__ == '__main__':
    unittest.main()