import gc

import Image_Enhancement
import ImagePreProcessing
import Region_Extraction
import Fiber_Density_Calculation
import os
import time
from PyQt5.QtCore import QThread

# sample for time delay of modules
test_delay = 1

# module steps return values
step_enhanced_image = None
step_bounded_input_image = None
bounded_binarized_input_image = None

# Output from "Fiber Density and Distribution" Module
densities = []
num_wedges = 0
num_rings = 0


# class SproutController (threading.Thread):
class SproutController (QThread):
    def __init__(self, ui, in_data):
        QThread.__init__(self)
        self.sprout_ui = ui
        self.in_data = in_data
        self.percent_count = 0

    def __del__(self):
        self.wait()

    def run(self):
        """
        Start the process thread that will run the Sprout Controller that calls Image Enhancement Module,
        Image Pre-Processing Module, Region Extraction Module, and  Fiber Density and Distribution Module.
        :return: None
        """

        global step_enhanced_image, step_bounded_input_image, num_rings, num_wedges, bounded_binarized_input_image

        print("--------------------------------------------")
        print("Sprout Controller: Acquired Input Parameters")
        print("--------------------------------------------")
        # print user input for testing
        print("User input:")
        print(" img_path = " + self.in_data['img_path'])
        print(" intermediate_path = " + self.in_data['intermediate_path'])
        print(" units = " + self.in_data['units'])
        print(" num_measurement = " + str(self.in_data['num_measurement']))
        print(" num_wedges = " + str(self.in_data['num_wedges']))
        print(" num_rings = " + str(self.in_data['num_rings']))
        print(" img_dpi = " + str(self.in_data['img_dpi']))
        print(" enhance = " + str(self.in_data['enhance']))

        time_start = time.time()

        # Create and change current working directory
        if not os.path.exists(self.in_data['intermediate_path']):
            try:
                os.makedirs(self.in_data['intermediate_path'])
                os.chdir(self.in_data['intermediate_path'])
            except OSError:
                self.sprout_ui.error_message = "Unable to create new intermediate path folder."
                self.sprout_ui.progressBar.setValue(2)
                return
        else:
            counter = 1
            # Verify if this path exists, if it does exist add a number after file name and verify again.
            # Continue this loop, increasing the appended number, until the file path does not exist.
            try:
                new_path = self.in_data['intermediate_path'] + str(counter)
                while os.path.exists(new_path):
                    new_path = self.in_data['intermediate_path'] + str(counter)
                    counter += 1

                print("New path " + new_path)
                os.makedirs(new_path)
                os.chdir(new_path)
            except Exception:
                self.sprout_ui.error_message = "Unable to create new intermediate path folder."
                self.sprout_ui.progressBar.setValue(2)
                return
        self.sprout_ui.save_window_ui.lineEdit_filePath.setText(os.getcwd())

        print("Current Working Directory:")
        print(" " + os.getcwd())

        # To aid with simulation for get_fiber_density
        num_rings = self.in_data['num_rings']
        num_wedges = self.in_data['num_wedges']

        if self.isInterruptionRequested():
            return

        # If image enhancement is required run Image Enhancement Module
        if self.in_data['enhance']:
            try:
                step_enhanced_image = Image_Enhancement.image_enhancement(self.in_data['img_path'])
            except Exception as e:
                self.sprout_ui.error_message = "Error in Image Enhancement:\n " + str(e)
                self.sprout_ui.progressBar.setValue(2)
                return
            self.update_progress_bar()
        else:
            step_enhanced_image = None;

        if self.isInterruptionRequested():
            return

        # Run Image Pre-processing Module
        try:
            bounded_binarized_input_image, step_bounded_input_image, = ImagePreProcessing.pre_process_image(
                self.in_data['num_measurement'],
                self.in_data['img_dpi'],
                self.in_data['units'],
                self.in_data['img_path'],
                step_enhanced_image,
                self)
        except Exception as e:
            self.sprout_ui.error_message = "Error in Image Pre-processing:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return
        self.update_progress_bar()

        if self.isInterruptionRequested():
            return

        # Run Region Extraction Module
        try:
            dictionary = Region_Extraction.region_extraction(step_bounded_input_image, bounded_binarized_input_image,
                                                             self.in_data['num_wedges'], self.in_data['num_rings'],
                                                             self)
        except Exception as e:
            self.sprout_ui.error_message = "Error in Region Extraction:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return
        self.update_progress_bar()

        if self.isInterruptionRequested():
            return

        # Run Fiber Density and Distribution Module
        try:
            Fiber_Density_Calculation.fiber_density_and_distribution(self.in_data['num_rings'],
                                                                     self.in_data['num_wedges'],
                                                                     dictionary)
        except Exception as e:
            self.sprout_ui.error_message = "Error in Fiber Density and Distribution:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return
        self.update_progress_bar()

        print("\n * Sprout Controller: Finished Successfully * ")
        print("      Total time: " + str(time.time() - time_start) + " sec")
        print("        Equal to: " + str((time.time() - time_start)/60) + " min")
        return

    def clear_mem(self):
        gc.collect()
        self.terminate()
        self.__del__()

    def update_progress_bar(self):
        """
        Update the progress bar by 25% if image enhancement is required other wais update by 33%
        :return: None
        """
        if self.in_data['enhance']:
            self.percent_count += 25
        else:
            self.percent_count += 33
            if self.percent_count == 99:
                self.percent_count += 1

        if self.percent_count >= 100:
            self.percent_count = 99

        self.sprout_ui.progressBar.setValue(self.percent_count)
        return
