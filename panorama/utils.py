# -*- coding: utf-8 -*-

"""
OS-related utils for python2/python3 compatibility
"""

from __future__ import unicode_literals, division, print_function

import sys
import os


if sys.version_info.major >= 3:
    # Python 3
    def path_exists(path):
        """Returns True if the given file or directory exists.  May raise
        exceptions, for instance if you don't have permission to stat()
        the given path.
        """
        try:
            os.stat(path)
            return True
        except FileNotFoundError:
            return False

    def makedirs(name, mode=0o777, exist_ok=False):
        """No-op wrapper around os.makedirs()"""
        return os.makedirs(name, mode=mode, exist_ok=exist_ok)

else:
    # Python 2
    def path_exists(path):
        """Returns True if the given file or directory exists.  May raise
        exceptions, for instance if you don't have permission to stat()
        the given path.
        """
        try:
            os.stat(path)
            return True
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
            else:
                raise

    def makedirs(name, mode=0o777, exist_ok=False):
        """Wrapper around os.makedirs() to support the python3-style "exist_ok"
        argument.
        """
        if not exist_ok:
            return os.makedirs(name, mode=mode)
        # Emulate exist_ok behaviour
        try:
            return os.makedirs(name, mode=mode)
        except OSError as e:
            if e.errno == os.errno.EEXIST:
                return
            else:
                raise
