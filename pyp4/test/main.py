#!/usr/bin/env python

import os
import unittest

def run():
    cur_path = os.path.abspath(__file__)
    cur_dir = os.path.dirname(cur_path)
    for name in os.listdir(cur_dir):
        name = os.path.splitext(name)[0]
        if name.startswith('test_'):
            unittest.main(module=__import__(name), verbosity=2)

if __name__ == '__main__':
    run()
