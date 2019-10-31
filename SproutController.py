import sys
import time
import threading

# User input data
in_data = {}

# Output from "Fiber Density and Distribution" Module
densities = []
measurement_data = {'avg_outer_diameter': 0,
                    'avg_inner_diameter': 0,
                    'area': 0,
                    'centroid': 0,
                    'moment_of_inertia': 0}

exitFlag = 0
test_delay = 2

class SproutController (threading.Thread):
    def __init__(self, sprout_ui, in_data):
        threading.Thread.__init__(self)
        self.sprout_ui = sprout_ui
        self.in_data = in_data
        self.percent_up = 0

    def run(self):
        global densities, measurement_data
        print("Sprout Controller: Acquired Input Parameters")
        print("--------------------------------------------")
        # print for testing
        print("img_path = " + self.in_data['img_path'])
        print("intermediate_path = " + self.in_data['intermediate_path'])
        print("units = " + self.in_data['units'])
        print("num_measurement = " + self.in_data['num_measurement'])
        print("num_wedges = " + self.in_data['num_wedges'])
        print("num_rings = " + self.in_data['num_rings'])
        print("img_dpi = " + self.in_data['img_dpi'])
        print("enhance = " + str(self.in_data['enhance']))

        if self.in_data['enhance']:
            self.image_enhancement_module()
            self.sprout_ui.update_progress_bar()

        self.image_pre_processing_module()
        self.sprout_ui.update_progress_bar()
        self.region_extraction_module()
        self.sprout_ui.update_progress_bar()
        self.fiber_density_distribution_module()
        self.sprout_ui.update_progress_bar()

        return

    def update_progress_bar(self):

        if self.in_data['enhance']:
            self.percent_up += 25
            self.sprout_ui.update_progress_bar(self.percent_up)
        else:
            self.percent_up += 33
            if self.percent_up == 99:
                self.percent_up += 1
            self.sprout_ui.update_progress_bar(self.percent_up)

        return

    def image_enhancement_module(self):
        print("\nImage Enhancement Module")
        print("------------------------")
        time.sleep(test_delay)
        return

    def image_pre_processing_module(self):
        print("\nImage Pre-processing Module")
        print("---------------------------")
        time.sleep(test_delay)
        return


    def region_extraction_module(self):
        print("\nRegion Extraction Module")
        print("------------------------")
        time.sleep(test_delay)
        return

    def fiber_density_distribution_module(self):
        print("\nFiber Density and Distribution")
        print("------------------------------")
        time.sleep(test_delay)
        return


def image_enhancement_module():
    print("\nImage Enhancement Module")
    print("------------------------")
    time.sleep(test_delay)
    return

def image_pre_processing_module():
    print("\nImage Pre-processing Module")
    print("---------------------------")
    time.sleep(test_delay)
    return


def region_extraction_module():
    print("\nRegion Extraction Module")
    print("------------------------")
    time.sleep(test_delay)
    return

def fiber_density_distribution_module():
    print("\nFiber Density and Distribution")
    print("------------------------------")
    time.sleep(test_delay)
    return
