#!/usr/bin/env python

import unittest
import types
import os
from pyp4.p4changelist import P4Changelist
from common.filesystem import create_path

class TestP4Changelist(unittest.TestCase):

    def setUp(self):
        self.__cl = P4Changelist()

    def tearDown(self):
        pass

    def test_chagnelist(self):
        self.__cl.new('foobar')
        self.assertIsNot(self.__cl.changelist, None)
        self.assertIsInstance(self.__cl.changelist, (types.IntType, types.StringTypes))
        self.assertEqual(self.__cl.description, 'foobar\n')

        cur_path = os.path.abspath(__file__)
        cur_dir = os.path.dirname(cur_path)
        new_files = []
        for i in range(3):
            path = os.path.join(cur_dir, 'foobar{0}'.format(i))
            create_path(path)
            new_files.append(path)
        self.__cl.add(new_files)
        self.assertEqual(self.__cl.files, new_files)
