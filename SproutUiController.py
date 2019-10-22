from PyQt5 import QtWidgets, uic, QtGui
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem, QInputDialog

# from PySide2 import QtGui
# from PySide2 import QtWidgets as sideWid
# from PySide2.QtCharts import QtCharts

from PyQt5.QtCore import QTimer

count_pb = 0
running = False

# messageBox_flag if true then there is a popup message in screen
wedges_messageBox_flag = False
rings_messageBox_flag = False

# input data
in_data = {'img_path': "",
           'intermediate_path': "",
           'units': "",
           'num_measurement': "0",
           'num_wedges': "0",
           'num_rings': "0",
           'img_dpi': "0",
           'enhance': "False"}

# columns: wedges, rows: rings (r1(w1,w2,...,w7,wAvg),r2(...),r3(...),rAvg(...))
densities = ((0.7500, 0.7100, 0.7000, 0.6800, 0.6900, 0.7000, 0.7500, 0.7200, 0.7125),
             (0.5000, 0.5500, 0.4900, 0.4500, 0.5000, 0.5100, 0.4700, 0.5300, 0.5000),
             (0.4500, 0.4400, 0.4000, 0.3800, 0.3500, 0.3900, 0.4500, 0.4200, 0.4100),
             (0.5667, 0.5667, 0.5300, 0.5033, 0.5133, 0.5333, 0.5567, 0.5567, 0.5408))

measurement_data = {'avg_outer_diameter': 8,
                    'avg_inner_diameter': 6,
                    'area': 22,
                    'centroid': 3,
                    'moment_of_inertia': 188.496}


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Sprout.ui', self)
        self.setWindowTitle("Sprout")

        self.ui()

    def ui(self):
        self.tabWidget_1.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.lineEdit_numMeasurements.setFocus(0)

        self.browse_button_1.clicked.connect(self.browse_file)
        self.browse_button_2.clicked.connect(self.browse_folder)

        self.lineEdit_numWedges.editingFinished.connect(self.update_num_wedges)
        self.lineEdit_numRings.editingFinished.connect(self.update_num_rings)

        self.start_button.clicked.connect(self.start_fiber_dencity_calc)
        self.save_button.clicked.connect(self.save_files)

        # progress bar details
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.runProgressBar)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.label_progressBar.hide()

        self.show()

    def update_num_wedges(self):
        global in_data, wedges_messageBox_flag, rings_messageBox_flag
        wedges_messageBox_flag = True
        temp = (self.lineEdit_numWedges.text(), 4, 100, self.label_numWedges.text())
        if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
            if not rings_messageBox_flag:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
            return

        temp = int(temp[0])*4
        self.label_numWedgesFeedback.setText("Num. Wedges: " + str(temp) + " @ {:.1f}º".format(360/temp))
        self.label_numRegionsFeedback.setText(str(temp*int(in_data['num_rings'])))
        in_data['num_wedges'] = str(temp)

    def update_num_rings(self):
        global in_data, wedges_messageBox_flag, rings_messageBox_flag
        rings_messageBox_flag = True
        temp = (self.lineEdit_numRings.text(), 1, 25, self.label_numRings.text())
        if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
            if not wedges_messageBox_flag:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
            return

        self.label_numRingsFeedback.setText(str(temp[0]))
        self.label_numRegionsFeedback.setText(str(int(temp[0])*int(in_data['num_wedges'])))
        in_data['num_rings'] = str(temp[0])

    def browse_file(self):
        url = QFileDialog.getOpenFileName(self, "Open a file", "", "All Files(*);;*.jpg; *jpeg;; *.png;; *bmp;; *tiff")
        self.lineEdit_imagePath.setText(url[0])
        cross_section = QPixmap(url[0])
        self.label_bamboo.setPixmap(cross_section)
        in_data['img_path'] = url[0]

    def browse_folder(self):
        url = QFileDialog.getExistingDirectory(self, "Open a directory", "", QFileDialog.ShowDirsOnly)
        self.lineEdit_intermediateStepPath.setText(url)
        in_data['intermediate_path'] = url

    def start_fiber_dencity_calc(self):
        global count_pb, running, in_data, densities, measurement_data
        # if program is currently in progress
        if running:
            # count_pb must be set to zero when the fiber density calculation is finished
            if count_pb == 0:
                self.dashboard_tab.setEnabled(True)
                self.tabWidget_2.setEnabled(True)
                self.graphs_tab.setEnabled(True)
                self.region_density_tab.setEnabled(True)

                # create graphs


                # create table
                i = 0
                j = 0
                column_name = []
                row_name = []

                self.tableWidget.setRowCount(len(densities))
                self.tableWidget.setColumnCount(len(densities[0]))

                for ring in densities:
                    for wedge in ring:
                        self.tableWidget.setItem(i, j, QTableWidgetItem("{:.4f}".format(wedge)))
                        j += 1
                    j = 0
                    i += 1

                for x in range(len(densities[0])):
                    if x == len(densities[0]) - 1:
                        column_name.append("Average " + str(x))
                    else:
                        column_name.append("Wedge " + str(x + 1))
                for x in range(len(densities)):
                    if x == len(densities[0]) - 1:
                        row_name.append("Average " + str(x))
                    else:
                        row_name.append("Ring " + str(x + 1))

                self.tableWidget.setHorizontalHeaderLabels(column_name)
                self.tableWidget.setVerticalHeaderLabels(row_name)
                self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

                # set measurement data
                self.lineEdit_avgOuterDiameter.setText(str(measurement_data['avg_outer_diameter']) + " cm")
                self.lineEdit_avgInnerDiameter.setText(str(measurement_data['avg_inner_diameter']) + " cm")
                self.lineEdit_area.setText(str(measurement_data['area']) + " cm^2")
                self.lineEdit_centroid.setText(str(measurement_data['centroid']) + " cm")
                self.lineEdit_momentOfInertia.setText(str(measurement_data['moment_of_inertia']) + " cm^4")

                self.tabWidget_1.setCurrentIndex(1)
                self.tabWidget_2.setCurrentIndex(0)

            self.browse_button_1.setEnabled(True)
            self.browse_button_2.setEnabled(True)
            self.comboBox_units.setEnabled(True)
            self.lineEdit_numMeasurements.setEnabled(True)
            self.lineEdit_numWedges.setEnabled(True)
            self.lineEdit_numRings.setEnabled(True)
            self.lineEdit_imageDPI.setEnabled(True)
            self.checkBox_imageEnhancement.setEnabled(True)

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
            # if(self.lineEdit_imagePath.text() is "" or self.lineEdit_intermediateStepPath.text() is "" or
            #         self.lineEdit_numWedges.text() is "" or self.lineEdit_numRings.text() is "" or
            #         self.lineEdit_numMeasurements.text() is "" or self.lineEdit_imageDPI.text() is ""):
            #     self.warning_message_box("Make sure all inputs are filled in.")
            #     return

            temp = (self.lineEdit_numMeasurements.text(), 4, 100, self.label_numMeasurements.text())
            if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
                return

            temp = (self.lineEdit_imageDPI.text(), 0, 2400, self.label_imageDPI.text())
            if not (str.isdigit(temp[0])) or int(temp[0]) > temp[2] or int(temp[0]) < temp[1]:
                self.warning_message_box(str(temp[3]) + "\nPlease input a number from "
                                         + str(temp[1]) + " to " + str(temp[2]))
                return

            # in_data['img_path'] = self.lineEdit_imagePath.text()
            # in_data['intermediate_path'] = self.lineEdit_intermediateStepPath.text()
            in_data['units'] = self.comboBox_units.currentText()
            in_data['num_measurement'] = str(int(self.lineEdit_numMeasurements.text())*4)
            # in_data['num_wedges'] = str(int(self.lineEdit_numWedges.text())*4)
            # in_data['num_rings'] = self.lineEdit_numRings.text()
            in_data['img_dpi'] = self.lineEdit_imageDPI.text()
            in_data['enhance'] = str(self.checkBox_imageEnhancement.isChecked())

            # print for testing
            print("img_path = " + in_data['img_path'])
            print("intermediate_path = " + in_data['intermediate_path'])
            print("units = " + in_data['units'])
            print("num_measurement = " + in_data['num_measurement'])
            print("num_wedges = " + in_data['num_wedges'])
            print("num_rings = " + in_data['num_rings'])
            print("img_dpi = " + in_data['img_dpi'])
            print("enhance = " + in_data['enhance'])

            self.browse_button_1.setEnabled(False)
            self.browse_button_2.setEnabled(False)
            self.comboBox_units.setEnabled(False)
            self.lineEdit_numMeasurements.setEnabled(False)
            self.lineEdit_numWedges.setEnabled(False)
            self.lineEdit_numRings.setEnabled(False)
            self.lineEdit_imageDPI.setEnabled(False)
            self.checkBox_imageEnhancement.setEnabled(False)

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
        global wedges_messageBox_flag, rings_messageBox_flag
        mbox = QMessageBox.information(self, "Warning!", message)
        if mbox == QMessageBox.Ok:
                self.lineEdit_numMeasurements.setFocus(0)
                rings_messageBox_flag = False
                wedges_messageBox_flag = False

    def save_files(self):
        mbox = QMessageBox.question(self, "Warning!", "Quiere Salvar?", QMessageBox.Save | QMessageBox.Cancel)
        if mbox == QMessageBox.Cancel:
                print("cancel")
        elif mbox == QMessageBox.Save:
            print("save")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
