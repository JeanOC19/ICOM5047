from PyQt5 import QtWidgets, uic, QtGui
import sys

from PyQt5.QtWidgets import QMessageBox, QFileDialog

from PySide2.QtCharts import QtCharts
from PyQt5.QtCore import QTimer

count_pb = 0
running = False

# input data
in_data = {'img_path': "",
           'intermediate_path': "",
           'units': "",
           'num_wedges': "",
           'num_rings': "",
           'num_measurement': "",
           'img_dpi': "",
           'enhance': ""}
# img_path = ""
# intermediate_path = ""
# units = ""
# num_wedges = 0
# num_rings = 0
# num_measurement = 0
# img_dpi = 0
# enhance = False


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Sprout.ui', self)
        self.setWindowTitle("Sprout")

        self.ui()

    def ui(self):
        self.browse_button_1.clicked.connect(self.browse_file)
        self.browse_button_2.clicked.connect(self.browse_folder)

        self.start_button.clicked.connect(self.start_fiber_dencity_calc)

        # progress bar details
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.runProgressBar)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.label_progressBar.hide()

        self.show()

    def browse_file(self):
        url = QFileDialog.getOpenFileName(self, "Open a file", "", "All Files(*);;*.jpg; *jpeg;; *.png;; *bmp;; *tiff")
        # print(url[0])
        in_data['img_path'] = url[0]
        self.lineEdit_imagePath.setText(url[0])

    def browse_folder(self):
        url = QFileDialog.getExistingDirectory(self, "Open a directory", "", QFileDialog.ShowDirsOnly)
        # print(url)
        in_data['intermediate_path'] = url
        self.lineEdit_intermediateStepPath.setText(url)

    def start_fiber_dencity_calc(self):
        global count_pb, running, in_data
        # if program is currently in progress
        if running:
            self.start_button.setStyleSheet("background-color: #539844;\nborder: 2px solid #444444;\n"
                                            "border-radius: 8px;\ncolor:white;\nfont: bold;")
            self.start_button.setText("Start")
            self.progressBar.hide()
            self.label_progressBar.hide()
            self.progressBar.setValue(0)

            count_pb = 0
            self.timer.stop()

            running = False
        # if program has not started
        else:
            if(self.lineEdit_imagePath.text() is "" or self.lineEdit_intermediateStepPath.text() is "" or
                    self.lineEdit_numWedges.text() is "" or self.lineEdit_numRings.text() is "" or
                    self.lineEdit_numMeasurements.text() is "" or self.lineEdit_imageDPI.text() is ""):
                self.warning_message_box("Make sure all inputs are filled in.")
                return

            temp = (self.lineEdit_numWedges.text(), 4, 100, self.label_numWedges.text())
            if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
                return

            temp = (self.lineEdit_numRings.text(), 1, 25, self.label_numRings.text())
            if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
                return

            temp = (self.lineEdit_imageDPI.text(), 0, 2400, self.label_imageDPI.text())
            if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
                return

            in_data['img_path'] = self.lineEdit_imagePath.text()
            in_data['intermediate_path'] = self.lineEdit_intermediateStepPath.text()
            in_data['units'] = self.comboBox_units.currentText()
            in_data['num_wedges'] = str(int(self.lineEdit_numWedges.text())*4)
            in_data['num_rings'] = self.lineEdit_numRings.text()
            in_data['num_measurement'] = str(int(self.lineEdit_numMeasurements.text())*4)
            in_data['img_dpi'] = self.lineEdit_imageDPI.text()
            in_data['enhance'] = str(self.checkBox_imageEnhancement.isChecked())

            # print for testing
            print("img_path = " + in_data['img_path'])
            print("intermediate_path = " + in_data['intermediate_path'])
            print("units = " + in_data['units'])
            print("num_wedges = " + in_data['num_wedges'])
            print("num_rings = " + in_data['num_rings'])
            print("num_measurement = " + in_data['num_measurement'])
            print("img_dpi = " + in_data['img_dpi'])
            print("enhance = " + in_data['enhance'])

            self.start_button.setStyleSheet("background-color: #da2a2a;\nborder: 2px solid #444444;\n"
                                            "border-radius: 8px;\ncolor:white;\nfont: bold;")
            self.start_button.setText("Stop")
            self.progressBar.show()
            self.label_progressBar.show()

            self.timer.start()
            running = True

    def runProgressBar(self):
        global count_pb
        count_pb += 5
        if count_pb > 100:
            count_pb = 0
            self.timer.stop()
            self.start_fiber_dencity_calc()
        else:
            self.progressBar.setValue(count_pb)

    def warning_message_box(self, message):
        QMessageBox.information(self, "Warning!", message)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
