import os
import threads
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWizard
from Resources.ui_db_wizard import Ui_wizard


class DBWizard(QWizard):
    def __init__(self, mainWindow, data_location, app_location, home_location, db_location, bowtie_location):
        QWizard.__init__(self)

        self.data_location = data_location
        self.app_location = app_location
        self.home_location = home_location
        self.db_location = db_location
        self.bowtie_location = bowtie_location

        self.ui_wizard = Ui_wizard()
        self.ui_wizard.setupUi(self)

        self.currentIdChanged.connect(self.create_database)
        self.ui_wizard.commandLinkButton_seq.clicked.connect(self.open_sequence_file)
        self.mainWindow = mainWindow

    def create_database(self):
        """Creates a Bowtie database."""
        self.iambusy = False

        if self.currentId() == 2:
            sequence_file_location = self.ui_wizard.label_5.text()
            db_name = self.ui_wizard.lineEdit.text()
            # Replace spaces, otherwise it makes problems with windows paths
            db_name = db_name.replace(' ', '_')

            if os.path.exists(sequence_file_location):
                if db_name != '':
                    self.step = 1
                    self.value = 0
                    self.button(self.FinishButton).setEnabled(False)
                    self.ui_wizard.progressBar.setValue(self.value)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                    # Start Bowtie thread
                    self.ui_wizard.label_3.setText('Creating Bowtie database. Please wait...')
                    self.ui_wizard.progressBar.setValue(self.value)
                    self.BowtieDBThread = threads.CreateDBThread(
                                                                str(sequence_file_location),
                                                                str(self.db_location),
                                                                str(db_name),
                                                                str(self.bowtie_location)
                                                                )

                    self.connect(self.BowtieDBThread, QtCore.SIGNAL("threadDone(QString, QString)"), self.thread_done)
                    self.BowtieDBThread.start()
                    self.BowtieDBThread.wait()

                else:
                    self.show_info_message("Please enter a database name.")
            else:
                self.show_info_message("Could not open sequence source file.")

            if os.path.exists(str(self.db_location) + str(db_name) + '.1.ebwt'):
                self.button(self.FinishButton).setEnabled(True)
                self.ui_wizard.progressBar.setValue(100)
                self.ui_wizard.label_3.setText('Database successfully created!')
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                self.show_info_message("Database could not be created.\nPlease check again your input file format.")

    def thread_done(self, info_message, bowtie_file_path):
        """Show message after thread has finished."""
        self.mainWindow.available_databases()

    def open_sequence_file(self):
        """Open a sequence file and return the path."""
        sequence_file_location = QtGui.QFileDialog.getOpenFileName(
                        self,
                        u"Open a sequence file",
                        self.home_location,
                        u"Sequence (*.fasta *.fas *.txt)")
        if not sequence_file_location.isNull():
            if os.path.exists(sequence_file_location):
                file_path = str(sequence_file_location)
                self.ui_wizard.label_5.setText(file_path)

    def show_info_message(self, message):
        QtGui.QMessageBox.information(self,
                    u"Information",
                    message
                    )