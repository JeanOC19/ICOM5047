import os
import sys
import time

from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtChart import QChart, QLineSeries, QScatterSeries, QChartView
from PyQt5.QtCore import pyqtSignal

import SproutController as Sprout
import Data_Management_Module as DM

# User input data
in_data = {'img_path': "",
           'intermediate_path': "",
           'units': "",
           'num_measurement': 0,
           'num_wedges': 0,
           'num_rings': 0,
           'img_dpi': 0,
           'enhance': False}
wedge_degree = 0

# Default values for the number of items that are present in the filter
# for the rings and wedges graphs (All, All Rings/Wedges, Average)
default_comboBox_graph_item_count = 3

# messageBox_flag: if true then there is a popup message in screen
measurement_messageBox_flag = False
wedges_messageBox_flag = False
rings_messageBox_flag = False
dpi_messageBox_flag = False

debounce = 0


class SproutUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(SproutUI, self).__init__()
        uic.loadUi('Sprout.ui', self)
        self.setWindowTitle("Sprout")
        self.setWindowIcon(QIcon('./Images/SproutIcon.ico'))

        self.get_default_path()

        self.save_window_ui = SaveWindow(self)

        self.chartView = None

        self.myThread = None
        # columns: wedges, rows: rings (r1(w1,w2,...,w7,wAvg),r2(...),r3(...),rAvg(...))
        self.densities = []
        self.measurement_data = []

        self.error_message = ""

        self.loading_image = QPixmap("./Images/LoadingImage")

    def ui(self):
        """
        Sets Sprout user interface and displays the user interface
        :return: None
        """
        self.tabWidget_1.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.lineEdit_numMeasurements.setFocus(0)

        # Main Screen and save button
        self.browse_button_1.clicked.connect(self.browse_file)
        self.browse_button_2.clicked.connect(self.browse_folder)
        self.lineEdit_intermediateStepPath.setText(in_data['intermediate_path'])

        self.lineEdit_numMeasurements.editingFinished.connect(self.update_num_diameter_measurements)
        self.lineEdit_numWedges.editingFinished.connect(self.update_num_wedges)
        self.lineEdit_numRings.editingFinished.connect(self.update_num_rings)
        self.lineEdit_imageDPI.editingFinished.connect(self.update_image_dpi)

        self.start_button.clicked.connect(self.start_button_func)
        self.stop_button.clicked.connect(self.stop_button_func)
        self.save_button.clicked.connect(self.show_save_files)

        # Graphs View
        self.comboBox_rings.currentIndexChanged.connect(self.filter_rings_graph)
        self.comboBox_wedges.currentIndexChanged.connect(self.filter_wedges_graph)

        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.label_progressBar.hide()

        self.disable_dashboard()

        self.progressBar.valueChanged.connect(self.progress_change)

        self.tabWidget_1.tabBar().setCursor(QtCore.Qt.PointingHandCursor)
        self.tabWidget_2.tabBar().setCursor(QtCore.Qt.PointingHandCursor)

        self.show()

    def get_default_path(self):
        """
        Gets the "Documents" directory of the user of the local computer.
        :return: None
        """
        temp = str(os.path.expanduser("~"))
        split = temp.split(os.path.sep)
        temp = str(split[0] + "/" + split[1] + "/" + split[2] + "/" + "Documents/Sprout/Run")
        in_data['intermediate_path'] = temp

    def browse_file(self):
        """
        Function mapped to the browse button used to select the file path of the image that will be used to
        calculate the fiber density of a bamboo cross-section.
        :return: None
        """
        url = QFileDialog.getOpenFileName(self, "Open a file", "", "*jpg; *jpeg;; *bmp;; *tif")

        if url[0] is not '':
            try:
                self.label_bamboo.setPixmap(self.loading_image)
                self.label_bamboo.repaint()
            except Exception:
                self.warning_message_box("Missing loading image. ")

            try:
                assert (url[0])[-4:] in ('.bmp', '.jpg', 'jpeg', '.tif'), "Image format is not supported."
            except Exception as e:
                self.label_bamboo.clear()
                self.warning_message_box(str(e))
                return

            try:
                cross_section = QPixmap(url[0])
                cross_section = cross_section.scaled(500, 500)
                if cross_section.isNull():
                    self.label_bamboo.clear()
                    self.warning_message_box("Unable to open input file.  \n\n")
                else:
                    self.label_bamboo.clear()
                    self.label_bamboo.setPixmap(cross_section)
                    self.lineEdit_imagePath.setText(url[0])
                    in_data['img_path'] = url[0]
            except Exception as e:
                self.label_bamboo.clear()
                self.warning_message_box("Unable to open input file, verify  \n file path or image file type.\n\n")

    def browse_folder(self):
        """
        Function mapped to the browse button used to select the folder path that will be used to
        save the intermediate step for the fiber density calculation.
        :return: None
        """
        url = QFileDialog.getExistingDirectory(self, "Open a directory", "", QFileDialog.ShowDirsOnly)
        if url is not '':
            self.lineEdit_intermediateStepPath.setText(url)
            in_data['intermediate_path'] = url

    def disable_dashboard(self):
        """
        Disables the dashboard and hides the graphs.
        :return: None
        """
        self.dashboard_tab.setEnabled(False)
        self.tabWidget_2.setEnabled(False)
        self.graphs_tab.setEnabled(False)
        self.region_density_tab.setEnabled(False)
        self.measurement_data_tab.setEnabled(False)

        self.tabWidget_2.setCurrentIndex(0)

        self.widget_rings.hide()
        self.widget_wedges.hide()
        self.comboBox_rings.hide()
        self.comboBox_wedges.hide()

    def update_num_diameter_measurements(self):
        """
        Update the value for the total number of measurements in the user interface main screen that serves as feedback.
        :return: None
        """
        global in_data

        if self.is_int_inbound(self.lineEdit_numMeasurements.text(), 3, 100):
            temp = int(self.lineEdit_numMeasurements.text()) * 4
            self.label_numMeasurementsFeedback.setText("Total Diameter Measurements: " + str(temp))
            in_data['num_measurement'] = temp
        else:
            self.lineEdit_numMeasurements.clear()

    def update_num_wedges(self):
        """
        Update the value for number of wedges in the user interface main screen that serves as feedback.
        :return: None
        """
        global in_data, wedge_degree

        if self.is_int_inbound(self.lineEdit_numWedges.text(), 3, 100):
            temp = int(self.lineEdit_numWedges.text()) * 4
            wedge_degree = 360 / temp
            self.label_numWedgesFeedback.setText("Num. Wedges: " + str(temp) + " @ {:.1f}º".format(wedge_degree))
            self.label_numRegionsFeedback.setText("Num. Regions: " + str(temp * int(in_data['num_rings'])))
            in_data['num_wedges'] = temp
        else:
            self.lineEdit_numWedges.clear()

    def update_num_rings(self):
        """
        Update the value for number of rings in the user interface main screen that serves as feedback.
        :return: None
        """
        global in_data

        temp = self.lineEdit_numRings.text()
        if self.is_int_inbound(temp, 1, 25):
            self.label_numRingsFeedback.setText("Num. Rings: " + str(temp))
            self.label_numRegionsFeedback.setText("Num. Regions: " + str(int(temp) * int(in_data['num_wedges'])))
            in_data['num_rings'] = int(temp)
        else:
            self.lineEdit_numRings.clear()

    def update_image_dpi(self):
        """
        Update the value for the image dpi (dot per inch) in the user interface main screen that serves as feedback.
        :return: None
        """
        global in_data

        if self.is_int_inbound(self.lineEdit_imageDPI.text(), 1200, 4800):
            temp = int(self.lineEdit_imageDPI.text())
            self.label_imageDPIFeedback.setText("Image DPI: " + str(temp))
            in_data['img_dpi'] = temp
        else:
            self.lineEdit_imageDPI.clear()

    def start_button_func(self):
        """
        Sets what the start button will do when it is pressed. It starts the fiber density calculation and
        disables user input. The button is replaced by the stop button.
        :return: None
        """
        global in_data, debounce
        # if program has not started
        if debounce is not 0:
            if (time.time() - debounce) < .30:
                return
            debounce = 0

        # Test input data for being empty
        if(self.lineEdit_imagePath.text() is "" or self.lineEdit_intermediateStepPath.text() is "" or
                self.lineEdit_numWedges.text() is "" or self.lineEdit_numRings.text() is "" or
                self.lineEdit_numMeasurements.text() is "" or self.lineEdit_imageDPI.text() is ""):
            self.warning_message_box("Make sure all inputs are filled in.")
            return

        # Test numeric input
        if not self.is_int_inbound(self.lineEdit_numMeasurements.text(), 3, 100, self.label_numMeasurements.text()):
            return
        if not self.is_int_inbound(self.lineEdit_numWedges.text(), 3, 100, self.label_numWedges.text()):
            return
        if not self.is_int_inbound(self.lineEdit_numRings.text(), 1, 25, self.label_numRings.text()):
            return
        if not self.is_int_inbound(self.lineEdit_imageDPI.text(), 1200, 4800, self.label_imageDPI.text()):
            return

        # After all inputs have been validated
        self.disable_dashboard()

        # Save input data in in_data dictionary
        in_data['units'] = self.comboBox_units.currentText()
        in_data['num_measurement'] = int(self.lineEdit_numMeasurements.text())*4
        in_data['img_dpi'] = int(self.lineEdit_imageDPI.text())
        in_data['enhance'] = bool(self.checkBox_imageEnhancement.isChecked())
        in_data['pixelMap'] = bool(self.checkBox_pixelMap.isChecked())

        self.inputs_set_enabled(False)

        self.progressBar.show()
        self.label_progressBar.show()
        self.progressBar.setValue(1)

        self.stop_button.setEnabled(True)
        self.start_button.hide()

        # Start Sprout Controller for fiber density calculation
        self.myThread = Sprout.SproutController(self, in_data)
        try:
            self.myThread.start()
            self.myThread.progress.connect(self.progressBar.setValue)
        except:
            self.warning_message_box("Error while starting process.")

    def stop_button_func(self):
        """
        Sets what the stop button will do when it is pressed or is called when the fiber density calculation
        is completed. It cancels the running session and enables user input. If running session is completed it
        enables the user input, and proceeds to display the dashboard (graphs, region density table, and measurement
         data). The button is replaced by the start button.
        :return: None
        """
        global debounce
        # if program is currently in progress

        self.stop_button.setEnabled(False)
        self.stop_button.repaint()

        if not self.myThread.isFinished():
            self.myThread.requestInterruption()
            self.myThread.wait()

        if self.progressBar.value() == 100:
            # if finished successfully

            # self.progressBar.setValue(100)
            self.dashboard_tab.setEnabled(True)
            self.tabWidget_2.setEnabled(True)
            self.graphs_tab.setEnabled(True)
            self.region_density_tab.setEnabled(True)
            self.measurement_data_tab.setEnabled(True)

            # create graphs
            self.create_graphs()

            # create table
            self.create_table()

            # set measurement data
            self.display_measurement_data()

            self.tabWidget_1.setCurrentIndex(1)
            self.tabWidget_2.setCurrentIndex(0)

        self.inputs_set_enabled(True)

        self.progressBar.hide()
        self.label_progressBar.hide()
        self.progressBar.setValue(0)

        self.start_button.show()
        debounce = time.time()

    def inputs_set_enabled(self, val: bool):
        """
        Enable or disable the options presented in the home screen depending on input parameter: val.
        :param val: True to anabel all the options in the home screen and False to disable.
        :return: None
        """
        self.browse_button_1.setEnabled(val)
        self.browse_button_2.setEnabled(val)
        self.comboBox_units.setEnabled(val)
        self.lineEdit_numMeasurements.setEnabled(val)
        self.lineEdit_numWedges.setEnabled(val)
        self.lineEdit_numRings.setEnabled(val)
        self.lineEdit_imageDPI.setEnabled(val)
        self.checkBox_imageEnhancement.setEnabled(val)
        self.checkBox_pixelMap.setEnabled(val)

        self.label_imagePath.setEnabled(val)
        self.label_intermediateStepPath.setEnabled(val)
        self.label_numMeasurements.setEnabled(val)
        self.label_numWedges.setEnabled(val)
        self.label_numRings.setEnabled(val)
        self.label_imageDPI.setEnabled(val)
        self.label_units.setEnabled(val)

    def create_graphs(self):
        """
        Creates the graphs that will be displayed int the dashboard's Graphs tab.
        :return: None
        """
        global default_comboBox_graph_item_count

        # Set Graphs ComboBox
        for x in range(self.comboBox_rings.count()):
            self.comboBox_rings.removeItem(default_comboBox_graph_item_count)

        for x in range(self.comboBox_wedges.count()):
            self.comboBox_wedges.removeItem(default_comboBox_graph_item_count)

        self.comboBox_rings.setCurrentIndex(0)
        self.comboBox_wedges.setCurrentIndex(0)

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
            if in_data['num_rings'] == 1:
                ring_series = QScatterSeries()
            else:
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

        if in_data['num_rings'] == 1:
            self.comboBox_rings.hide()
        else:
            self.comboBox_rings.show()
        self.comboBox_wedges.show()

    def filter_rings_graph(self):
        """
        Filters the rings graph by: All(includes average), All Wedges(only rings are shown),
        Average(only average is shown), and individual rings(varies depending on number of rings).
        :return: None
        """
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

    def filter_wedges_graph(self):
        """
        Filters the wedges graph by: All(includes average), All Wedges(only wedges are shown),
        Average(only average is shown), and individual wedges(varies depending on number of wedges).
        :return: None
        """
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
        """
        Creates the table that will be presented in the dashboard's Region Density tab
        based on fiber density calculations.
        :return: None
        """
        i = 0
        j = 0
        column_name = []
        row_name = []

        self.tableWidget.setRowCount(len(self.densities))
        self.tableWidget.setColumnCount(len(self.densities[0]))

        for ring in self.densities:
            for wedge in ring:
                item = QTableWidgetItem("{:.4f}".format(wedge))
                item.setTextAlignment(Qt.AlignCenter)

                # if average of average
                if j == (len(self.densities[0])-1) and i == (len(self.densities)-1):
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)

                self.tableWidget.setItem(i, j, item)
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
        """
        Manages all output data related to the measurement data that is presented in the dashboard Measurement Data.
        :return: None
        """
        self.lineEdit_area.setText(str("{:.4f}".format(self.measurement_data[0])) + " " + in_data['units'] + "^2")
        self.lineEdit_avgOuterDiameter.setText(str("{:.4f}".format(self.measurement_data[1])) + " " + in_data['units'])
        self.lineEdit_avgInnerDiameter.setText(str("{:.4f}".format(self.measurement_data[2])) + " " + in_data['units'])
        self.lineEdit_AverageT.setText(str("{:.4f}".format(self.measurement_data[3])) + " " + in_data['units'])
        self.lineEdit_centroid_x.setText(str("{:.4f}".format(self.measurement_data[4])) + " " + in_data['units'])
        self.lineEdit_centroid_y.setText(str("{:.4f}".format(self.measurement_data[5])) + " " + in_data['units'])
        self.lineEdit_momentOfInertia_x.setText(str("{:.4f}".format(self.measurement_data[6])) + " " +
                                                in_data['units'] + "^4")
        self.lineEdit_momentOfInertia_y.setText(str("{:.4f}".format(self.measurement_data[7])) + " " +
                                                in_data['units'] + "^4")
        self.lineEdit_productOfInertia.setText(str("{:.4f}".format(self.measurement_data[8])) + " " +
                                               (in_data['units']) + "^4")

    def is_int_inbound(self, ui_in: str, lower: int, upper: int, ui_in_name: str = None):
        """
        Test if user input is in specified upper and lower bound, including upper and lower bound value.
        :param ui_in: user input for value that will be tested
        :param lower: lowest value that ui_in can have to return True
        :param upper: highest value that ui_in can hava to return True
        :param ui_in_name: user input label name that is used in popup messages for users to relate error
        :return: True if ui_in is in upper and lower bound (lower <= ui_in <= upper)
                    otherwise False
        """
        if not (str.isdigit(ui_in)) or int(ui_in) > upper or int(ui_in) < lower:
            if ui_in_name is not None:
                self.warning_message_box(str(ui_in_name) + "\nPlease input a number from "
                                         + str(lower) + " to " + str(upper))
            return False
        else:
            return True

    def warning_message_box(self, message):
        """
        Display a popup message box to inform users of error.
        :param message: Message to be displayed in the popup message
        :return:
        """
        mbox = QMessageBox.critical(self, "Warning!!", message)
        if mbox == QMessageBox.Ok:
            self.lineEdit_numMeasurements.setFocus(0)

    def show_save_files(self):
        """
        Call to displays the popup for the Save Popup Window.
        :return: None
        """
        self.windowModality()
        self.save_window_ui.lineEdit_filePath.setText(os.getcwd())
        self.save_window_ui.show()
        self.save_window_ui.raise_()

    def progress_change(self):
        """
        Signals the user interface when process is completed or wen error occurs.
        :return: None
        """
        if self.progressBar.value() == 2:
            self.stop_button_func()
            self.warning_message_box(str(self.error_message))
        elif self.progressBar.value() == 100:
            self.densities = DM.get_fiber_density_average()
            self.measurement_data = DM.get_dimensional_measurements()
            self.stop_button_func()


class SaveWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(SaveWindow, self).__init__(parent)
        uic.loadUi('SproutSave.ui', self)
        self.setWindowTitle("Save Files")
        self.setWindowIcon(QIcon('./Images/SproutIcon.ico'))

        self.ui()

    def ui(self):
        """
        Sets the ui for the save popup window.
        :return: None
        """
        # Set button function
        self.browse_button_3.clicked.connect(self.browse_folder)
        self.save_button.clicked.connect(self.save_graph_data)
        self.cancel_button.clicked.connect(self.cancel_save_graph_data)

        # Set default values
        self.checkBox_data.setChecked(True)

    def browse_folder(self):
        """
        Mapped to the button that allows user to select the folder where graphs or data will be saved.
        :return: None
        """
        url = QFileDialog.getExistingDirectory(self, "Open a directory", "", QFileDialog.ShowDirsOnly)
        if url is not '':
            self.lineEdit_filePath.setText(url)

    def save_graph_data(self):
        """
        Starts the process of saving the graphs and/or data calling the respective function in the data
        management module.
        :return: None
        """
        if not (self.checkBox_graphs.isChecked() or self.checkBox_data.isChecked()):
            QMessageBox.critical(self, "Warning!", "Please make sure to have at least   \n"
                                                             " one checkbox selected.")
        elif self.lineEdit_fileName.text().strip() is "":
            QMessageBox.critical(self, "Warning!", "Please make sure to provide a valid file name. Do not   \n"
                                                   " leave blank and do not use special character (<, >, :,  \n"
                                                   " /, , |, ?, *, \").  ")
        elif self.lineEdit_filePath.text() is "":
            QMessageBox.critical(self, "Warning!", "Please make sure to provide a folder path.   ")
        else:
            save_folder_file_path = self.lineEdit_filePath.text()
            save_file_name = self.lineEdit_fileName.text().strip()

            special_characters = ['<', '>', ':', '/', '\\', '|', '?', '*', '"']
            for c in special_characters:
                if c in save_file_name:
                    QMessageBox.critical(self, "Warning!", "Please make sure to provide a valid file name. Do not   \n"
                                                   " leave blank and do not use special character (<, >, :,  \n"
                                                   " /, , |, ?, *, \").  ")
                    return
            try:
                if self.checkBox_graphs.isChecked():
                    DM.save_graphs(save_file_name, save_folder_file_path)
                if self.checkBox_data.isChecked():
                    DM.save_fiber_density_csv(save_file_name, save_folder_file_path)
                    DM.save_dimensional_measurements_csv(save_file_name, save_folder_file_path, in_data['units'])
                    if in_data['pixelMap'] is True:
                        DM.save_pixel_table(save_file_name, save_folder_file_path)

                # Close save window
                self.close()

                # Open save location
                try:
                    os.startfile(save_folder_file_path)
                except OSError:
                    raise Exception("Unable to save \"File Path\" location.")

            except Exception as e:
                QMessageBox.critical(self, "Warning!", str(e))

    def cancel_save_graph_data(self):
        """
        Maps what the cancel button does: that is close save popup window.
        :return: None
        """
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SproutUI()
    window.ui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
