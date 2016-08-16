#!/usr/bin/env python

import logging
import types

"""
Having the ability to add more handlers. e.g. command handlers. P4V's log window
only logs commands and their results.
Also it would be nice to log everything to a file as the user chooses so.
Telemetry can be the next bigger step if we want analize something.
"""

class _P4Logger(logging.getLoggerClass()):

    CMD = 15

    def cmd(self, msg):
        """
        This can be hooked up to a Qt signal/slot system to prompt results in a
        GUI. e.g. P4V's log panel.
        """
        cmd = msg
        if isinstance(msg, (types.ListType, types.TupleType)):
            cmd = ' '.join(msg)
        self.log(self.CMD, cmd)

def _get_logger():
    formatter = logging.Formatter('[%(asctime)s] (%(levelname)s) %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.setLoggerClass(_P4Logger)
    logging.addLevelName(_P4Logger.CMD, 'CMD')
    logger = logging.getLogger('pyp4logging')
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)
    return logger

p4log = _get_logger()

if __name__ == '__main__':
    p4log.cmd('foobar\nfff')
    p4log.log(22, 'test')
