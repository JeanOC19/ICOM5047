import gc

import Image_Enhancement
import ImagePreProcessing
import Region_Extraction
import Fiber_Density_Calculation
import os
import time
from PyQt5.QtCore import QThread, pyqtSignal

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
    progress = pyqtSignal(int, name="update_progress")

    def __init__(self, ui, in_data):
        QThread.__init__(self)
        self.sprout_ui = ui
        self.in_data = in_data

        # progress bar and module percent weight
        self.percent_count = 0
        self.p_img_enhancement_percent = 10
        self.p_img_pre_processing = (43, 48)
        self.p_region_extraction = (43, 48)
        self.p_fiber_density_and_distribution = 4

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
        print(" Pixel Map = " + str(self.in_data['pixelMap']))

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

        print("Current Working Directory:")
        print(" " + os.getcwd())

        # To aid with simulation for get_fiber_density
        num_rings = self.in_data['num_rings']
        num_wedges = self.in_data['num_wedges']

        # Check if has an interrupt request (Stop Button Interrupt)
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
            self.update_progress_bar(self.p_img_enhancement_percent)
        else:
            step_enhanced_image = None

        # Check if has an interrupt request (Stop Button Interrupt)
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
                self,
                self.in_data['pixelMap'])
        except Exception as e:
            self.sprout_ui.error_message = "Error in Image Pre-processing:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return

        # Check if has an interrupt request (Stop Button Interrupt)
        if self.isInterruptionRequested():
            return

        # Run Region Extraction Module
        try:
            region_dictionary = Region_Extraction.region_extraction(step_bounded_input_image, bounded_binarized_input_image,
                                                             self.in_data['num_wedges'], self.in_data['num_rings'], self)
        except Exception as e:
            self.sprout_ui.error_message = "Error in Region Extraction:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return

        # Check if has an interrupt request (Stop Button Interrupt)
        if self.isInterruptionRequested():
            return

        # Run Fiber Density and Distribution Module
        try:
            Fiber_Density_Calculation.fiber_density_and_distribution(self.in_data['num_rings'],
                                                                     self.in_data['num_wedges'],
                                                                     region_dictionary)
        except Exception as e:
            self.sprout_ui.error_message = "Error in Fiber Density and Distribution:\n " + str(e)
            self.sprout_ui.progressBar.setValue(2)
            return
        self.update_progress_bar(self.p_fiber_density_and_distribution)

        print("\n * Sprout Controller: Finished Successfully * ")
        print("      Total time: " + str(time.time() - time_start) + " sec")
        print("        Equal to: " + str((time.time() - time_start)/60) + " min")
        return


    def update_progress_bar(self, percent: int):
        """
        Update the progress bar by indicated percent.
        :param percent: indicated percent to increase
        :return: None
        """
        self.percent_count += percent
        self.progress.emit(self.percent_count)
        return

    def update_module_progress(self, weight, internal_percent_completed: int):
        """
        Updates the progress bar by a given percent for the calling module. Calling module must indicate it's
        corresponding default weight (defined in thread initialization).
        :param weight: default percent weight of the module calling the function
        :param internal_percent_completed: percent of completion of the module that is calling the function
        :return: None
        """
        if self.in_data['enhance']:
            self.percent_count += weight[0] * internal_percent_completed/100
        else:
            self.percent_count += weight[1] * internal_percent_completed/100

        self.progress.emit(self.percent_count)
        return
