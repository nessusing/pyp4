import os
import unittest

if __name__ == '__main__':
    """
    Unittest entry point for this module.
    It searches every .py file under the ./unittest folder
    that starts with "test_", and run them through unittest.

    Order of tests is not guaranteed, merely the order returned
    by os.listdir()
    """
    thisfile = os.path.realpath(__file__)
    root = os.path.dirname(thisfile)
    for filename in os.listdir(root):
        name, ext = os.path.splitext(filename)
        if name.startswith('test_') and ext == '.py':
            unittest.main(module=name)
