import os
import time
from PyQt5.QtCore import QThread


# Output from "Fiber Density and Distribution" Module


# sample for time delay of modules
test_delay = 1

# module steps return values
step_enhanced_image = None
step_bounded_input_image = None
bounded_binarized_input_image = None


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
        global step_enhanced_image
        print("--------------------------------------------")
        print("Sprout Controller: Acquired Input Parameters")
        print("--------------------------------------------")
        # print for testing
        print("User input:")
        print(" img_path = " + self.in_data['img_path'])
        print(" intermediate_path = " + self.in_data['intermediate_path'])
        print(" units = " + self.in_data['units'])
        print(" num_measurement = " + str(self.in_data['num_measurement']))
        print(" num_wedges = " + str(self.in_data['num_wedges']))
        print(" num_rings = " + str(self.in_data['num_rings']))
        print(" img_dpi = " + str(self.in_data['img_dpi']))
        print(" enhance = " + str(self.in_data['enhance']))

        print("Current Working Directory:")
        print(" " + os.getcwd())

        if self.in_data['enhance']:
            step_enhanced_image = image_enhancement(self.in_data['img_path'])
            self.update_progress_bar()

        step_bounded_input_image, bounded_binarized_input_image = pre_process_image(self.in_data['num_measurement'],
            self.in_data['img_dpi'], self.in_data['units'], self.in_data['img_path'], step_enhanced_image)
        self.update_progress_bar()

        region_extraction(step_bounded_input_image, bounded_binarized_input_image, self.in_data['num_wedges'],
                          self.in_data['num_rings'])
        self.update_progress_bar()

        fiber_density_and_distribution(self.in_data['num_wedges'], self.in_data['num_rings'])
        self.update_progress_bar()

        print(" * Finished Successfully * ")
        return

    def update_progress_bar(self):
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


def image_enhancement(image_path: str):
    enhanced_image = "\n        _  \n" \
                       "      /   \\  \n"\
                       "      \\ _ /    "

    print("\n------------------------")
    print("Image Enhancement Module")
    print("------------------------")

    print("Input Parameters:")
    print(" image_path: " + image_path)

    print("Output Data:")
    print("enhanced_image: " + enhanced_image)

    time.sleep(test_delay)
    return enhanced_image


def pre_process_image(num_of_measurements: int, image_dpi: int, units: str, image_path=None, enhanced_image=None):
    bounded_input_image = "\n    |   _   |\n" \
                            "    | /   \\ | \n"\
                            "    | \\ _ / |    "
    bounded_binarized_input_image = "black or white"

    print("\n---------------------------")
    print("Image Pre-processing Module")
    print("---------------------------")

    print("Input Parameters:")
    print(" num_of_measurements: " + str(num_of_measurements))
    print(" image_dpi: " + str(image_dpi))
    print(" units: " + units)
    print(" image_path: " + str(image_path))
    print(" enhanced_image: " + str(enhanced_image))

    print("Output Data:")
    print(" bounded_input_image: " + bounded_input_image)
    print(" bounded_binarized_input_image: " + bounded_binarized_input_image)

    time.sleep(test_delay)
    return bounded_input_image, bounded_binarized_input_image


def region_extraction(bounded_input_image: object, bounded_binarized_input_image: object,
                      number_wedges: int, number_rings: int):
    print("\n------------------------")
    print("Region Extraction Module")
    print("------------------------")

    print("Input Parameters:")
    print(" bounded_input_image: " + bounded_input_image)
    print(" bounded_binarized_input_image: " + bounded_binarized_input_image)
    print(" number_wedges: " + str(number_wedges))
    print(" number_rings: " + str(number_rings))

    print("Output Data:")
    print(" None ")

    time.sleep(test_delay)
    return


def fiber_density_and_distribution(number_rings: int, number_wedges: int):
    print("\n------------------------------")
    print("Fiber Density and Distribution")
    print("------------------------------")

    print("Input Parameters:")
    print(" number_rings: " + str(number_rings))
    print(" number_wedges: " + str(number_wedges))

    print("Output Data:")
    print(" None ")

    time.sleep(test_delay)
    return


def get_dimensional_measurements():
    measurement_data = [22, 8, 6, 3, 3, 188.496, 188.496, -1.3]
    print("\n-------------------------")
    print("Get Dimensional Measurement")
    print("---------------------------")

    print("Input Parameters:")
    print(" None")

    print("Output Data:")
    print(" Area: " + str(measurement_data[0]))
    print(" Avg Outer Diameter: " + str(measurement_data[1]))
    print(" Avg Inner Diameter: " + str(measurement_data[2]))
    print(" Centroid x: " + str(measurement_data[3]))
    print(" Centroid y: " + str(measurement_data[4]))
    print(" Moment of Inertia x: " + str(measurement_data[5]))
    print(" Moment of Inertia y: " + str(measurement_data[6]))
    print(" Product of Inertia: " + str(measurement_data[7]))

    return measurement_data


def get_fiber_density():
    densities = [[0.4500, 0.4400, 0.4000, 0.3800, 0.3500, 0.3900, 0.4500, 0.4200, 0.4100],
                 [0.5000, 0.5500, 0.4900, 0.4500, 0.5000, 0.5100, 0.4700, 0.5300, 0.5000],
                 [0.7500, 0.7100, 0.7000, 0.6800, 0.6900, 0.7000, 0.7500, 0.7200, 0.7125],
                 [0.5667, 0.5667, 0.5300, 0.5033, 0.5133, 0.5333, 0.5567, 0.5567, 0.5408]]
    print("\n-------")
    print("Densities")
    print("---------")

    print("Input Parameters:")
    print(" None")

    print("Output Data:")
    print(" densities: " + str(densities))
    return densities

