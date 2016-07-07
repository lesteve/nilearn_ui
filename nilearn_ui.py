import sys

try:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    sip.setapi('QUrl', 2)
    from formlayout.formlayout import QApplication
    PYQT = True
except ImportError:
    PYQT = False

def use_qt_backend():
    from qtbackend.nilearn_main import NilearnMainWindow
    app = QApplication(sys.argv)
    nmw = NilearnMainWindow()
    nmw.show()
    sys.exit(app.exec_())


def use_tk_backend():
    raise NotImplementedError("Should be implemented")


if __name__ == '__main__':
    if PYQT:
        use_qt_backend()
    else:
        use_tk_backend()
