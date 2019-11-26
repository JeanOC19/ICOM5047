import Image_Enhancement
import ImagePreProcessing
import Region_Extraction
import Fiber_Density_Calculation
import Data_Management_Module
import unittest
import os
import psutil
import Sprout

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


class MyTestCase(unittest.TestCase):
    def test_sample_0(self):
        parameters = {'img_path': 'C:/Users/jeano/PycharmProjects/ICOM5047/Images/R_0.0.0.jpg',
                      'intermediate_path': "Run1",
                      'num_measurement': 12,
                      'num_wedges': 12,
                      'units': 'cm',
                      'num_rings': 3,
                      'img_dpi': 1200,
                      'enhance': 0
                      }

        controller = SproutController(parameters)
        controller.run()
        density = Data_Management_Module.get_fiber_density_average()[-1][-1]
        print(density)
        measurements = Data_Management_Module.get_dimensional_measurements()
        print(measurements)
        self.assertLessEqual(calculate_error(measurements[0], 16.2273), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[1], 6.6696), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[2], 4.8683), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[3], 3.2406), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[4], 3.4100), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[5], 25.9764), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[6], 34.5381), 3.5, "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[7], -1.2249), 3.5, "Product of inertia calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(density, 0.56394), 3.5, "Area calculation has more than 3.5% of error")

    def test_sample_1(self):
        parameters = {'img_path': 'C:/Users/jeano/PycharmProjects/ICOM5047/Images/R_1.1.1.jpg',
                      'intermediate_path': "Run2",
                      'num_measurement': 12,
                      'num_wedges': 12,
                      'units': 'in',
                      'num_rings': 3,
                      'img_dpi': 1800,
                      'enhance': 0
                      }

        controller = SproutController(parameters)
        controller.run()
        density = Data_Management_Module.get_fiber_density_average()[-1][-1]
        print(density)
        measurements = Data_Management_Module.get_dimensional_measurements()
        print(measurements)
        self.assertLessEqual(calculate_error(measurements[0], 3.902), 3.5,
                             "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[1], 2.955), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[2], 1.956), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[3], 1.5011), 3.5,
                             "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[4], 1.4572), 3.5,
                             "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[5], 2.3856), 3.5,
                             "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[6], 2.2770), 3.5,
                             "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[7], 0.13438), 3.5,
                             "Product of inertia calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(density, 0.4491), 3.5, "Area calculation has more than 3.5% of error")

    def test_sample_2(self):
        parameters = {'img_path': 'C:/Users/jeano/PycharmProjects/ICOM5047/Images/2400dpi.jpg',
                      'intermediate_path': "Run3",
                      'num_measurement': 12,
                      'num_wedges': 24,
                      'units': 'cm',
                      'num_rings': 3,
                      'img_dpi': 2400,
                      'enhance': 0
                      }

        controller = SproutController(parameters)
        controller.run()
        density = Data_Management_Module.get_fiber_density_average()[-1][-1]
        print(density)
        measurements = Data_Management_Module.get_dimensional_measurements()
        self.assertLessEqual(calculate_error(measurements[0], 10.7366), 3.5,
                             "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[1], 6.3156), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[2], 5.1202), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[3], 3.1771), 3.5,
                             "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[4], 3.1654), 3.5,
                             "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[5], 27.5068), 3.5,
                             "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[6], 29.5814), 3.5,
                             "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[7], 0.5871), 3.5,
                             "Product of inertia calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(density, 0.53688), 3.5, "Area calculation has more than 3.5% of error")

    def test_sample_3(self):
        parameters = {'img_path': 'C:/Users/jeano/PycharmProjects/ICOM5047/Images/4800dpi.jpg',
                      'intermediate_path': "Run4",
                      'num_measurement': 12,
                      'num_wedges': 24,
                      'units': 'cm',
                      'num_rings': 3,
                      'img_dpi': 4800,
                      'enhance': 0
                      }

        controller = SproutController(parameters)
        controller.run()
        density = Data_Management_Module.get_fiber_density_average()[-1][-1]
        print(density)
        measurements = Data_Management_Module.get_dimensional_measurements()
        self.assertLessEqual(calculate_error(measurements[0], 10.8041), 3.5,
                             "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[1], 6.3167), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[2], 5.1197), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[3], 3.1689), 3.5,
                             "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[4], 3.1572), 3.5,
                             "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[5], 30.7145), 3.5,
                             "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[6], 33.2111), 3.5,
                             "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(measurements[7], 0.6567), 3.5,
                             "Product of inertia calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(density, 0.53688), 3.5, "Area calculation has more than 3.5% of error")


class SproutController ():
    def __init__(self, in_data):
        self.in_data = in_data
        self.percent_count = 0

    def run(self):
        """
        Start the process thread that will run the Sprout Controller that calls Image Enhancement Moduel,
        Image Pre-Processing Module, Region Extraction Module, and  Fiber Density and Distribution Moduel.
        :return: None
        """

        global step_enhanced_image, step_bounded_input_image, num_rings, num_wedges

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

        if not os.path.exists(self.in_data['intermediate_path']):
            try:
                os.makedirs(self.in_data['intermediate_path'])
            except:
                raise Exception("Unable to create intermediate path folder")

        os.chdir(self.in_data['intermediate_path'])

        print("Current Working Directory:")
        print(" " + os.getcwd())

        # To aid with simulation for get_fiber_density
        num_rings = self.in_data['num_rings']
        num_wedges = self.in_data['num_wedges']

        # If image enhancement is required run Image Enhancement Module
        if self.in_data['enhance']:
            try:
                step_enhanced_image = Image_Enhancement.image_enhancement(self.in_data['img_path'])
            except Exception as e:
                print("Error in Image Enhancement:\n " + str(e))
                return
            self.update_progress_bar()

        # Run Image Pre-processing Module
        try:
            bounded_binarized_input_image, step_bounded_input_image, = ImagePreProcessing.pre_process_image(
                self.in_data['num_measurement'],
                self.in_data['img_dpi'],
                self.in_data['units'],
                self.in_data['img_path'],
                step_enhanced_image)
            process = psutil.Process(os.getpid())
            print(process.memory_info().rss / 1000000, "MB")
        except Exception as e:
            print("Error in Image Pre-processing:\n " + str(e))
            return
        self.update_progress_bar()

        # Run Region Extraction Module
        dictionary = Region_Extraction.region_extraction(step_bounded_input_image, bounded_binarized_input_image,
                                                             self.in_data['num_wedges'],
                                                             self.in_data['num_rings'])

        self.update_progress_bar()

        # Run Fiber Density and Distribution Module
        try:
            Fiber_Density_Calculation.fiber_density_and_distribution(self.in_data['num_rings'],
                                                                     self.in_data['num_wedges'],
                                                                     dictionary)
        except Exception as e:
            print("Error in Fiber Density and Distribution:\n " + str(e))
            return

        self.update_progress_bar()

        print("\n * Sprout Controller: Finished Successfully * ")
        return

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

        print(self.percent_count)
        return


def calculate_error(measure, actual):
    return (abs(actual - measure)/actual) * 100


if __name__ == '__main__':
    unittest.main()
