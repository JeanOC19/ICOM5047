import os
import sys

from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtChart import QChart, QLineSeries, QChartView

import SproutController as Sprout

# messageBox_flag if true then there is a popup message in screen
wedges_messageBox_flag = False
rings_messageBox_flag = False

# input data
in_data = {'img_path': "",
           'intermediate_path': "",
           'units': "",
           'num_measurement': 0,
           'num_wedges': 0,
           'num_rings': 0,
           'img_dpi': 0,
           'enhance': False}

# default values
default_comboBox_graph_item_count = 3


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Sprout.ui', self)
        self.setWindowTitle("Sprout")

        self.save_window_ui = SaveWindow()
        self.chartView = None

        self.is_running = False

        self.myThread = None
        # columns: wedges, rows: rings (r1(w1,w2,...,w7,wAvg),r2(...),r3(...),rAvg(...))
        self.densities = []
        self.measurement_data = []

        # self.ui()

    def ui(self):
        self.tabWidget_1.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.lineEdit_numMeasurements.setFocus(0)

        # Main Screen and save button
        self.browse_button_1.clicked.connect(self.browse_file)
        self.browse_button_2.clicked.connect(self.browse_folder)

        self.lineEdit_numWedges.editingFinished.connect(self.update_num_wedges)
        self.lineEdit_numRings.editingFinished.connect(self.update_num_rings)

        self.start_button.clicked.connect(self.start_button_func)
        self.save_button.clicked.connect(self.save_files)

        # Graphs View
        self.comboBox_rings.currentIndexChanged.connect(self.change_rings_graph)
        self.comboBox_wedges.currentIndexChanged.connect(self.change_wedges_graph)

        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.label_progressBar.hide()

        self.comboBox_rings.hide()
        self.comboBox_wedges.hide()

        self.progressBar.valueChanged.connect(self.progress_change)

        self.tabWidget_1.tabBar().setCursor(QtCore.Qt.PointingHandCursor)
        self.tabWidget_2.tabBar().setCursor(QtCore.Qt.PointingHandCursor)

        self.show()

    def progress_change(self):
        if self.progressBar.value() == 99:
            self.myThread.wait()
            self.densities = Sprout.get_fiber_density()
            self.measurement_data = Sprout.get_dimensional_measurements()
            self.start_button_func()

    def terminate_thread(self):
        if self.myThread is not None:
            print(" - - killing thread")
            self.myThread.terminate()
            self.myThread.wait()

    def is_int_inbound(self, ui_in: str, lower: int, upper: int, ui_in_name: str):
        if not (str.isdigit(ui_in)) or int(ui_in) > upper or int(ui_in) < lower:
            self.warning_message_box(str(ui_in_name) + "\nPlease input a number from "
                                     + str(lower) + " to " + str(upper))
            return False
        else:
            return True

    def update_num_wedges(self):
        global in_data, wedges_messageBox_flag, rings_messageBox_flag
        if rings_messageBox_flag:
            return
        wedges_messageBox_flag = True

        if self.is_int_inbound(self.lineEdit_numWedges.text(), 3, 100, self.label_numWedges.text()):
            temp = int(self.lineEdit_numWedges.text()) * 4
            self.label_numWedgesFeedback.setText("Num. Wedges: " + str(temp) + " @ {:.1f}º".format(360 / temp))
            self.label_numRegionsFeedback.setText(str(temp * int(in_data['num_rings'])))
            wedges_messageBox_flag = False
            in_data['num_wedges'] = temp

    def update_num_rings(self):
        global in_data, wedges_messageBox_flag, rings_messageBox_flag
        if wedges_messageBox_flag:
            return
        rings_messageBox_flag = True

        temp = self.lineEdit_numRings.text()
        if self.is_int_inbound(temp, 1, 25, self.label_numRings.text()):
            self.label_numRingsFeedback.setText(str(temp))
            self.label_numRegionsFeedback.setText(str(int(temp) * int(in_data['num_wedges'])))
            rings_messageBox_flag = False
            in_data['num_rings'] = temp

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

    def start_button_func(self):
        global in_data

        # if program is currently in progress
        if self.is_running:
            self.terminate_thread()
            # if finished successfully
            if self.progressBar.value() == 99:
                self.progressBar.setValue(100)
                self.dashboard_tab.setEnabled(True)
                self.tabWidget_2.setEnabled(True)
                self.graphs_tab.setEnabled(True)
                self.region_density_tab.setEnabled(True)

                # create graphs
                self.create_graphs()

                # create table
                self.create_table()

                # set measurement data
                self.display_measurement_data()

                self.tabWidget_1.setCurrentIndex(1)
                self.tabWidget_2.setCurrentIndex(0)

            self.inputs_set_enabled(True)

            self.start_button.setStyleSheet("QPushButton{\nbackground-color: #539844;\nborder: 2px solid #444444;\n"
                                            "border-radius: 8px;\ncolor:white;\nfont: bold;\n}")
            self.start_button.setText("Start")
            self.progressBar.hide()
            self.label_progressBar.hide()
            self.progressBar.setValue(0)

            self.is_running = False

        # if program has not started
        else:
            if(self.lineEdit_imagePath.text() is "" or self.lineEdit_intermediateStepPath.text() is "" or
                    self.lineEdit_numWedges.text() is "" or self.lineEdit_numRings.text() is "" or
                    self.lineEdit_numMeasurements.text() is "" or self.lineEdit_imageDPI.text() is ""):
                self.warning_message_box("Make sure all inputs are filled in.")
                return

            if not self.is_int_inbound(self.lineEdit_numMeasurements.text(), 3, 100, self.label_numMeasurements.text()):
                return
            if not self.is_int_inbound(self.lineEdit_numWedges.text(), 3, 100, self.label_numWedges.text()):
                return
            if not self.is_int_inbound(self.lineEdit_numRings.text(), 1, 25, self.label_numRings.text()):
                return
            if not self.is_int_inbound(self.lineEdit_imageDPI.text(), 25, 4800, self.label_imageDPI.text()):
                return

            try:
                os.chdir(in_data['intermediate_path'])
            except OSError:
                QMessageBox.information(self, "Warning!", "File path not found for intermediate steps. ")
                return

            in_data['units'] = self.comboBox_units.currentText()
            in_data['num_measurement'] = int(self.lineEdit_numMeasurements.text())*4
            in_data['img_dpi'] = int(self.lineEdit_imageDPI.text())
            in_data['enhance'] = bool(self.checkBox_imageEnhancement.isChecked())

            self.inputs_set_enabled(False)

            self.start_button.setStyleSheet("QPushButton{\nbackground-color: #da2a2a;\nborder: 2px solid #444444;\n"
                                            "border-radius: 8px;\ncolor:white;\nfont: bold;\n}")
            self.start_button.setText("Stop")
            self.progressBar.show()
            self.label_progressBar.show()
            self.progressBar.setValue(1)

            self.is_running = True

            # Start Sprout Controller for fiber density calculation
            try:
                self.myThread = Sprout.SproutController(self, in_data)
            except:
                print("** myThread create failed **")
            try:
                self.myThread.start()
            except :
                print("** qthread fail **")

    def inputs_set_enabled(self, val):
        self.browse_button_1.setEnabled(val)
        self.browse_button_2.setEnabled(val)
        self.comboBox_units.setEnabled(val)
        self.lineEdit_numMeasurements.setEnabled(val)
        self.lineEdit_numWedges.setEnabled(val)
        self.lineEdit_numRings.setEnabled(val)
        self.lineEdit_imageDPI.setEnabled(val)
        self.checkBox_imageEnhancement.setEnabled(val)

        self.label_imagePath.setEnabled(val)
        self.label_intermediateStepPath.setEnabled(val)
        self.label_numMeasurements.setEnabled(val)
        self.label_numWedges.setEnabled(val)
        self.label_numRings.setEnabled(val)
        self.label_imageDPI.setEnabled(val)
        self.label_units.setEnabled(val)

    def create_graphs(self):
        global default_comboBox_graph_item_count

        # Set Ring ComboBox
        for x in range(self.comboBox_rings.count()):
            if x >= default_comboBox_graph_item_count:
                self.comboBox_rings.removeItem(default_comboBox_graph_item_count)

        # Set Wedges ComboBox
        for x in range(self.comboBox_wedges.count()):
            if x >= default_comboBox_graph_item_count:
                self.comboBox_wedges.removeItem(default_comboBox_graph_item_count)

        # Ring Graph
        self.ring_chart = QChart()

        for x in range(len(self.densities)):
            ring_series = QLineSeries()
            for y in range(len(self.densities[x])-1):
                ring_series.append(y+1, self.densities[x][y])
            self.ring_chart.addSeries(ring_series)
            if x < len(self.densities)-1:
                self.comboBox_rings.addItem("Ring " + str(x+1))

        self.ring_chart.setTitle('Fiber Density VS Wedges')
        self.ring_chart.legend().hide()
        self.ring_chart.createDefaultAxes()
        self.ring_chart.axes(Qt.Horizontal)[0].setRange(1, len(self.densities[0])-1)
        self.ring_chart.axes(Qt.Vertical)[0].setRange(0, 1)
        self.ring_chart.axes(Qt.Horizontal)[0].setTitleText("Wedge Number")
        self.ring_chart.axes(Qt.Vertical)[0].setTitleText("Fiber Density")

        self.chartView = QChartView(self.ring_chart, self.widget_rings)
        self.chartView.resize(self.widget_rings.size())

        # Wedges Graph
        self.wedge_chart = QChart()

        for y in range(len(self.densities[0])):
            ring_series = QLineSeries()
            for x in range(len(self.densities)-1):
                ring_series.append(x+1, self.densities[x][y])
            self.wedge_chart.addSeries(ring_series)
            if y < len(self.densities[0])-1:
                self.comboBox_wedges.addItem("Wedge " + str(y+1))

        self.wedge_chart.setTitle('Fiber Density VS Rings')
        self.wedge_chart.legend().hide()
        self.wedge_chart.createDefaultAxes()
        if (len(self.densities)) == 2:
            self.wedge_chart.axes(Qt.Horizontal)[0].setRange(0, 2)
        else:
            self.wedge_chart.axes(Qt.Horizontal)[0].setRange(1, len(self.densities)-1)
        self.wedge_chart.axes(Qt.Vertical)[0].setRange(0, 1)
        self.wedge_chart.axes(Qt.Horizontal)[0].setTitleText("Ring Number")
        self.wedge_chart.axes(Qt.Vertical)[0].setTitleText("Fiber Density")

        self.chartView = QChartView(self.wedge_chart, self.widget_wedges)
        self.chartView.resize(self.widget_wedges.size())

        self.widget_rings.show()
        self.widget_wedges.show()

        self.comboBox_rings.show()
        self.comboBox_wedges.show()

    def change_rings_graph(self):
        global default_comboBox_graph_item_count

        for x in range(len(self.ring_chart.series())):
            self.ring_chart.series()[x].show()

        if self.comboBox_rings.currentText() == "All Rings":
            for x in range(len(self.ring_chart.series()) - 1):
                self.ring_chart.series()[x].show()
            self.ring_chart.series()[len(self.ring_chart.series()) - 1].hide()
        elif self.comboBox_rings.currentText() == "Average":
            for x in range(len(self.ring_chart.series()) - 1):
                self.ring_chart.series()[x].hide()
            self.ring_chart.series()[len(self.ring_chart.series()) - 1].show()
        elif "Ring" in self.comboBox_rings.currentText():
            for x in range(len(self.ring_chart.series())):
                self.ring_chart.series()[x].hide()
            self.ring_chart.series()[self.comboBox_rings.currentIndex() - default_comboBox_graph_item_count].show()

    def change_wedges_graph(self):
        global default_comboBox_graph_item_count

        for x in range(len(self.wedge_chart.series())):
            self.wedge_chart.series()[x].show()

        if self.comboBox_wedges.currentText() == "All Wedges":
            for x in range(len(self.wedge_chart.series()) - 1):
                self.wedge_chart.series()[x].show()
            self.wedge_chart.series()[len(self.wedge_chart.series()) - 1].hide()
        elif self.comboBox_wedges.currentText() == "Average":
            for x in range(len(self.wedge_chart.series()) - 1):
                self.wedge_chart.series()[x].hide()
            self.wedge_chart.series()[len(self.wedge_chart.series()) - 1].show()
        elif "Wedge" in self.comboBox_wedges.currentText():
            for x in range(len(self.wedge_chart.series())):
                self.wedge_chart.series()[x].hide()
            self.wedge_chart.series()[self.comboBox_wedges.currentIndex() - default_comboBox_graph_item_count].show()

    def create_table(self):
        i = 0
        j = 0
        column_name = []
        row_name = []

        self.tableWidget.setRowCount(len(self.densities))
        self.tableWidget.setColumnCount(len(self.densities[0]))

        for ring in self.densities:
            for wedge in ring:
                self.tableWidget.setItem(i, j, QTableWidgetItem("{:.4f}".format(wedge)))
                j += 1
            j = 0
            i += 1

        for x in range(len(self.densities[0])):
            if x == len(self.densities[0]) - 1:
                column_name.append("Average")
            else:
                column_name.append("Wedge " + str(x + 1))
        for y in range(len(self.densities)):
            if y == len(self.densities) - 1:
                row_name.append("Average")
            else:
                row_name.append("Ring " + str(y + 1))

        self.tableWidget.setHorizontalHeaderLabels(column_name)
        self.tableWidget.setVerticalHeaderLabels(row_name)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def display_measurement_data(self):
        self.lineEdit_area.setText(str(self.measurement_data[0]) + " " + in_data['units'] + "^2")
        self.lineEdit_avgOuterDiameter.setText(str(self.measurement_data[1]) + " " + in_data['units'])
        self.lineEdit_avgInnerDiameter.setText(str(self.measurement_data[2]) + " " + in_data['units'])
        self.lineEdit_centroid_x.setText(str(self.measurement_data[3]) + " " + in_data['units'])
        self.lineEdit_centroid_y.setText(str(self.measurement_data[4]) + " " + in_data['units'])
        self.lineEdit_momentOfInertia_x.setText(str(self.measurement_data[5]) + " " + in_data['units'] + "^4")
        self.lineEdit_momentOfInertia_y.setText(str(self.measurement_data[6]) + " " + in_data['units'] + "^4")
        self.lineEdit_productOfInertia.setText(str(self.measurement_data[7]) + " " + in_data['units'] + "^4")

    def warning_message_box(self, message):
        global wedges_messageBox_flag, rings_messageBox_flag
        mbox = QMessageBox.information(self, "Warning!", message)
        if mbox == QMessageBox.Ok:
                self.lineEdit_numMeasurements.setFocus(0)
                rings_messageBox_flag = False
                wedges_messageBox_flag = False

    def save_files(self):
        self.windowModality()
        self.save_window_ui.show()
        self.save_window_ui.raise_()


class SaveWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SaveWindow, self).__init__()
        uic.loadUi('SproutSave.ui', self)
        self.setWindowTitle("Save Files")

        self.ui()

    def ui(self):
        self.browse_button_3.clicked.connect(self.browse_folder)
        self.save_button.clicked.connect(self.save_graph_data)
        self.cancel_button.clicked.connect(self.cancel_save_graph_data)
        self.checkBox_graphs.setChecked(True)

    def browse_folder(self):
        url = QFileDialog.getExistingDirectory(self, "Open a directory", "", QFileDialog.ShowDirsOnly)
        self.lineEdit_filePath.setText(url)

    def save_graph_data(self):
        save_file_name = ""
        save_folder_file_path = ""

        if not (self.checkBox_graphs.isChecked() or self.checkBox_data.isChecked()):
            QMessageBox.information(self, "Warning!", "Please make sure to have at least   \n"
                                                             " one checkbox selected.")
        elif self.lineEdit_fileName.text().strip() is "":
            QMessageBox.information(self, "Warning!", "Please make sure to provide a file name.   ")
        elif self.lineEdit_filePath.text() is "":
            QMessageBox.information(self, "Warning!", "Please make sure to provide a folder path.   ")
        else:
            save_folder_file_path = self.lineEdit_filePath.text()
            save_file_name = self.lineEdit_fileName.text().strip()
            if self.checkBox_graphs.isChecked():
                Sprout.save_graphs(save_file_name, save_folder_file_path)
            if self.checkBox_data.isChecked():
                Sprout.save_fiber_density_csv(save_file_name, save_folder_file_path)
                Sprout.save_dimensional_measurements_csv(save_file_name, save_folder_file_path, in_data['units'])
            self.close()

    def cancel_save_graph_data(self):
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.ui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
