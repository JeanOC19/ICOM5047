import Image_Enhancement
import ImagePreProcessing
import Region_Extraction
import Fiber_Density_Calculation
import os
import time


class SproutController():
    def __init__(self, ui, in_data):
        self.sprout_ui = ui
        self.in_data = in_data
        self.percent_count = 0

    def run(self):
        """
        Start the process thread that will run the Sprout Controller that calls Image Enhancement Moduel,
        Image Pre-Processing Moduel, Region Extraction Module, and  Fiber Density and Distribution Moduel.
        :return: None
        """
        global step_enhanced_image, step_bounded_input_image, num_rings, num_wedges
        step_enhanced_image = None

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
            step_enhanced_image = Image_Enhancement.image_enhancement(self.in_data['img_path'])
            self.update_progress_bar()

        # Run Image Pre-processing Module
        bounded_binarized_input_image, step_bounded_input_image,  = ImagePreProcessing.pre_process_image(
            self.in_data['num_measurement'],
            self.in_data['img_dpi'],
            self.in_data['units'],
            self.in_data['img_path'],
            step_enhanced_image)
        self.update_progress_bar()

        # Run Region Extraction Module
        dictionary = Region_Extraction.region_extraction(step_bounded_input_image, bounded_binarized_input_image,
                                            self.in_data['num_wedges'],
                                            self.in_data['num_rings'])
        self.update_progress_bar()

        # Run Fiber Density and Distribution Module
        Fiber_Density_Calculation.fiber_density_calculation(self.in_data['num_rings'], self.in_data['num_wedges'], dictionary)
        self.update_progress_bar()

        print("\n * Sprout Controller: Finished Successfully * ")
        return

    def update_progress_bar(self):
        print('Updated progress bar')


if __name__ == '__main__':

    parameters = {'img_path': 'C:/Users/jeano/PycharmProjects/ICOM5047/Images/R_0.0.0.jpg',
                  'intermediate_path': "Run1",
                  'num_measurement': 12,
                  'num_wedges': 12,
                  'units': 'cm',
                  'num_rings': 3,
                  'img_dpi': 1200,
                  'enhance': 1
                  }
    startt = time.process_time()
    controller = SproutController(None, parameters)
    controller.run()

    print("Total time: " + str(time.process_time() - startt))
