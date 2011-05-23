# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The log dockwindow.
"""

from __future__ import unicode_literals

from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QAction, QKeySequence

import actioncollection
import actioncollectionmanager
import app
import panels


class LogTool(panels.Panel):
    """A dockwidget showing the log of running Jobs."""
    def __init__(self, mainwindow):
        super(LogTool, self).__init__(mainwindow)
        self.hide()
        self.toggleViewAction().setShortcut(QKeySequence("Meta+Alt+L"))
        ac = self.actionCollection = Actions()
        ac.log_next_error.triggered.connect(self.slotNextError)
        ac.log_previous_error.triggered.connect(self.slotPreviousError)
        actioncollectionmanager.manager(mainwindow).addActionCollection(ac)
        mainwindow.addDockWidget(Qt.BottomDockWidgetArea, self)
        app.jobStarted.connect(self.slotJobStarted)
        app.jobFinished.connect(self.slotJobFinished)
    
    def translateUI(self):
        self.setWindowTitle(_("LilyPond Log"))
        self.toggleViewAction().setText(_("LilyPond &Log"))
        
    def createWidget(self):
        from . import logwidget
        return logwidget.LogWidget(self)
    
    def slotJobStarted(self, doc, job):
        """Called whenever job starts, decides whether to follow it and show the log."""
        if doc == self.mainwindow().currentDocument() or self.mainwindow() == jobattributes.get(job).mainwindow:
            self.widget().switchDocument(doc)
            if QSettings().value("log/show_on_start", True) not in (False, "false"):
                self.show()

    def slotJobFinished(self, document, job, success):
        if not success and document == self.mainwindow().currentDocument():
            self.show()
    
    def slotNextError(self):
        """Jumps to the position pointed to by the next error message."""
        self.widget().gotoError(1)
    
    def slotPreviousError(self):
        """Jumps to the position pointed to by the next error message."""
        self.widget().gotoError(-1)
        

class Actions(actioncollection.ActionCollection):
    name = "logtool"
    def createActions(self, parent=None):
        self.log_next_error = QAction(parent)
        self.log_previous_error = QAction(parent)
        
        self.log_next_error.setShortcut(QKeySequence("Ctrl+E"))
        self.log_previous_error.setShortcut(QKeySequence("Ctrl+Shift+E"))
        
    def translateUI(self):
        self.log_next_error.setText(_("Next Error Message"))
        self.log_previous_error.setText(_("Previous Error Message"))


# log errors by initializing Errors instance
@app.jobStarted.connect
def _log_errors(document):
    from . import errors
    errors.errors(document)

