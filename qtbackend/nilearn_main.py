import sys
import collections
import threading
import Queue
import time
import os.path as osp
import tempfile

from formlayout.formlayout import (FormWidget,
                                   FormTabWidget,
                                   FormComboWidget,
                                   MainContainerMixin)

from PyQt4 import QtGui
from PyQt4.QtCore import (Qt, QUrl, pyqtSignal)

from PyQt4.QtWebKit import QWebView

from scripts import COMPUTATIONS, FUNCTIONS

from report import prepare_report_directory
from qtbackend.decorators import busy


class ReportWidget(QtGui.QWidget):
    def __init__(self, url, parent=None):
        super(ReportWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        self.web = QWebView()
        layout.addWidget(self.web)
        self.load_url(url)

    def load_url(self, url):
        self.web.load(QUrl(url))


def _suppress_tooltips(results):
    """suppress tool tips in results dictionnary keys"""
    for key in results.keys():
        val = results.pop(key)
        results[key.split('::')[0]] = val


class ComputationForm(QtGui.QWidget, MainContainerMixin):
    result = 'dict'
    type = 'form'
    def __init__(self, parent=None, comment=None):
        super(ComputationForm, self).__init__(parent)
        self.float_fields = []
        layout = QtGui.QVBoxLayout(self)
        self.stacked_widget = QtGui.QStackedWidget(self)
        layout.addWidget(self.stacked_widget)
        self.computation_names = sorted(COMPUTATIONS.keys())
        for algo in self.computation_names:
            descr = COMPUTATIONS[algo]
            if isinstance(descr[0][0], (list, tuple)):
                formwidget = FormTabWidget(descr, comment=comment,
                                           parent=self)
            elif len(descr[0]) == 3:
                formwidget = FormComboWidget(descr, comment=comment,
                                             parent=self)
            else:
                formwidget = FormWidget(descr, comment=comment,
                                        parent=self)
            formwidget.setup()
            self.stacked_widget.addWidget(formwidget)
        self.bbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.bbox.button(QtGui.QDialogButtonBox.Ok).setText("Run")
        layout.addWidget(self.bbox)

    def register_float_field(self, field):
        self.float_fields.append(field)

    def get(self):
        """ return values of current widget"""
        computation_name = self.computation_names[self.stacked_widget.currentIndex()]
        datalist = COMPUTATIONS[computation_name]
        adict = collections.OrderedDict(datalist)
        print self.stacked_widget.currentWidget()
        result = self.stacked_widget.currentWidget().get()
        _suppress_tooltips(result)
        if result:
            result['verbose'] = int(result.get('verbose', 0))
            print 'result: ', result
            return result

    def setCurrentIndex(self, index):
        self.stacked_widget.setCurrentIndex(index)


class ComputationWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ComputationWidget, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout(self)
        self.report = ReportWidget('', parent=self)
        layout.addWidget(self.report)
        # self.form.bbox.accepted.connect(self.do_run)

    def _get_computation_func(self, queue):
        computation_name = self.parent().current_simulation()
        computation_func = FUNCTIONS[computation_name]
        def secure_computation_func(params):
            try:
                results = computation_func(params)
            except Exception, err:
                queue.put(('txt',
                           'An error occured during computation\n % s' % err))
            else:
                queue.put(results)
        return secure_computation_func

    def do_run(self, params):
        stdout, stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = self.parent().progress_reporter
            sys.stderr = self.parent().progress_reporter
            queue = Queue.Queue()
            compute_thread = threading.Thread(target=self._get_computation_func(queue),
                                              args=(params,))
            compute_thread.start()
            while compute_thread.isAlive():
                QtGui.QApplication.instance().processEvents()
                time.sleep(0.3)
            compute_thread.join()
            results = queue.get()
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        if results[0] == 'txt':
            print "DONE : ", results[1]
        elif results[0] == 'file':
            print "DONE :", results[1]
            self.report.web.load(QUrl(results[1]))


class ProgessReporter(QtGui.QTextEdit):
    do_append = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProgessReporter, self).__init__(parent=parent, readOnly=True)
        font = QtGui.QFont("Courier New")
        font.setFixedPitch(True)
        self.setFont(font)
        # we use a queued connection since a write may come from another thread
        self.do_append.connect(self.append, type=Qt.QueuedConnection)

    def write(self, value):
        self.do_append.emit(value)


class NilearnMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(NilearnMainWindow, self).__init__()
        self.computation_names = sorted(COMPUTATIONS.keys())
        self.computation_widget = ComputationWidget(self)
        self.setCentralWidget(self.computation_widget)
        self.create_dockwindows()
        self.create_menu()

    def create_dockwindows(self):
        algo_selection = QtGui.QDockWidget("Algorithms selection", self)
        algo_selection.setAllowedAreas(Qt.RightDockWidgetArea |
                                       Qt.LeftDockWidgetArea)
        self.splitter = QtGui.QSplitter(algo_selection)
        self.splitter.setOrientation(Qt.Vertical)
        self.algos = QtGui.QListWidget(self.splitter)
        self.algos.addItems(self.computation_names)
        self.algos.setSelectionMode(1)
        self.form = ComputationForm(self.splitter)
        algo_selection.setWidget(self.splitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, algo_selection)
        self.algos.currentRowChanged.connect(
            self.form.setCurrentIndex)
        self.algos.currentRowChanged.connect(self.show_documentation)
        self.algos.setCurrentRow(0)
        self.form.bbox.accepted.connect(self.do_run)
        progress = QtGui.QDockWidget("Progression logs", self)
        progress.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.progress_reporter = ProgessReporter(self)
        progress.setWidget(self.progress_reporter)
        self.addDockWidget(Qt.BottomDockWidgetArea, progress)

    def create_menu(self):
        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit application')
        quitAction.triggered.connect(QtGui.qApp.quit)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(quitAction)

    def current_simulation(self):
        return self.algos.currentItem().text()

    @busy
    def do_run(self):
        self.computation_widget.do_run(self.form.get())

    def show_documentation(self):
        print "call show documentation"
        computation_name = self.current_simulation()
        computation_func = FUNCTIONS[computation_name]
        documentation = computation_func.__doc__
        if not documentation:
            return
        try:
            from report.numpydoc import get_report_from_doc
            directory = tempfile.mkdtemp(prefix='tmp_nilearn_doc')
            filename = osp.join(directory, 'doc.html')
            prepare_report_directory(directory)
            print '#'*20
            print directory
            print '#'*20
            report = get_report_from_doc(documentation)
            report.save_html(filename)
            self.computation_widget.report.load_url(filename)
        except ImportError:
            import traceback
            traceback.print_exc()

