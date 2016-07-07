# -*- coding: utf-8 -*-
"""
Helper decorators functions
"""

from PyQt4 import QtGui as qt
from PyQt4.QtCore import Qt

def busy(func):
    """Use an hourglass cursor during execution of the function

    Careful with Qt slots, as the *args can cause too many arguments
    to be passed to the function

    :param func:

    """
    def busywrapped(*args, **kwargs):
        """

        :param *args:
        :param **kwargs:

        """
        qt.QApplication.setOverrideCursor(qt.QCursor(Qt.WaitCursor))
        qt.QApplication.processEvents()
        try:
            return func(*args, **kwargs)
        finally:
            qt.QApplication.restoreOverrideCursor()
            qt.QApplication.processEvents()

    busywrapped.__doc__ = func.__doc__
    return busywrapped
