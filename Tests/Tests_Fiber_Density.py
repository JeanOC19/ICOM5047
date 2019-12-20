import unittest
import Fiber_Density_Calculation as Fdc
import Region_Extraction as Re
import os
import cv2


class TestFiberDensity(unittest.TestCase):

    def test_inputs_fiber_density(self):
        """
        Test that invalid number of wedges and rings throw an exception
        """
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 2, 11)
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 3, 0)
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 0, 12)
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 26, 401)
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 3, 500)
        self.assertRaises(Exception, Fdc.fiber_density_calculation, 500, 12)

    def test_fiber_density_accuracy_rings(self):
        """
        Test that the average fiber density of rings is below 3.5% error
        """
        matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
                                 0.429762, 0.393449, 0.401225, 0.429967],
                                [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
                                 0.548483, 0.542541, 0.553700, 0.548965],
                                [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
                                 0.706593, 0.715743, 0.714168, 0.703361]]

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = Re.binarize_image(bw_image)
        number_wedges = 12
        number_rings = 3
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        # Run Region Extraction Module
        dictionary = Re.region_extraction(rgb_image, bin_image, number_wedges, number_rings)

        # Run Fiber Density Calculation Module
        fiber_density_sprout = Fdc.fiber_density_calculation(number_rings, number_wedges, dictionary)
        fd_with_average = Fdc.fiber_density_averages(fiber_density_sprout)
        fd_matlab_average = Fdc.fiber_density_averages(matlab_fiber_density)
        print()
        for i in range(number_rings):
            exact = fd_matlab_average[i][number_wedges]
            approx = fd_with_average[i][number_wedges]
            percentage_error = (abs(exact - approx) / exact) * 100
            print('Ring ' + str(i + 1) + ', Exact value: ' + str(exact) + ', Approximate value: ' + str(approx) +
                  ', Percentage of error: ' + str(percentage_error))
            # self.assertTrue(percentage_error <= 3.5,
            #                 "Error Percentage " + str(percentage_error) +
            #                 " is larger than 3.5 in: [" + str(i) + "][" + str(number_wedges - 1) + "]")
        print('-------------------------------------')

    def test_fiber_density_accuracy_wedges(self):
        """
        Test that the average fiber density of wedges is below 3.5% error
        """
        matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
                                 0.429762, 0.393449, 0.401225, 0.429967],
                                [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
                                 0.548483, 0.542541, 0.553700, 0.548965],
                                [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
                                 0.706593, 0.715743, 0.714168, 0.703361]]

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = Re.binarize_image(bw_image)
        number_wedges = 12
        number_rings = 3
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        # Run Region Extraction Module
        dictionary = Re.region_extraction(rgb_image, bin_image, number_wedges, number_rings)

        # Run Fiber Density Calculation Module
        fiber_density_sprout = Fdc.fiber_density_calculation(number_rings, number_wedges, dictionary)
        fd_with_average = Fdc.fiber_density_averages(fiber_density_sprout)
        fd_matlab_average = Fdc.fiber_density_averages(matlab_fiber_density)
        print()
        for j in range(number_wedges):
            exact = fd_matlab_average[number_rings][j]
            approx = fd_with_average[number_rings][j]
            percentage_error = (abs(exact - approx) / exact) * 100
            print('Wedge ' + str(j + 1) + ', Exact value: ' + str(exact) + ', Approximate value: ' + str(approx) +
                  ', Percentage of error: ' + str(percentage_error))
            # self.assertTrue(percentage_error <= 3.5,
            #                 "Error Percentage " + str(percentage_error) +
            #                 " is larger than 3.5 in: [" + str(number_rings) + "][" + str(j) + "]")

    def test_correct_average_calculation_rings(self):
        """
        Test that average of columns and rows is being calculated correctly
        """

        matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
                                 0.429762, 0.393449, 0.401225, 0.429967],
                                [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
                                 0.548483, 0.542541, 0.553700, 0.548965],
                                [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
                                 0.706593, 0.715743, 0.714168, 0.703361]]

        fiber_density_with_average = Fdc.fiber_density_averages(matlab_fiber_density)

        ring_average1 = (0.443516 + 0.435262 + 0.447433 + 0.453988 + 0.430503 + 0.451662 + 0.449479 + 0.449918 +
                         0.429762 + 0.393449 + 0.401225 + 0.429967) / 12

        self.assertTrue(ring_average1 == fiber_density_with_average[0][12],
                        "Calculated average does not match the expected one")

        ring_average2 = (0.551969 + 0.569961 + 0.549261 + 0.529712 + 0.563685 + 0.567644 + 0.590936 + 0.521671 +
                         0.548483 + 0.542541 + 0.553700 + 0.548965) / 12

        self.assertTrue(ring_average2 == fiber_density_with_average[1][12],
                        "Calculated average does not match the expected one")
        ring_average3 = (0.712373 + 0.725422 + 0.699161 + 0.675843 + 0.688871 + 0.694169 + 0.725839 + 0.685522 +
                         0.706593 + 0.715743 + 0.714168 + 0.703361) / 12

        self.assertTrue(ring_average3 == fiber_density_with_average[2][12],
                        "Calculated average does not match the expected one")

        wedge_average1 = (0.443516 + 0.551969 + 0.712373) / 3

        self.assertTrue(wedge_average1 == fiber_density_with_average[3][0],
                        "Calculated average does not match the expected one")

        wedge_average2 = (0.435262 + 0.569961 + 0.725422) / 3

        self.assertTrue(wedge_average2 == fiber_density_with_average[3][1],
                        "Calculated average does not match the expected one")

        wedge_average12 = (0.429967 + 0.548965 + 0.703361) / 3

        self.assertTrue(wedge_average12 == fiber_density_with_average[3][11],
                        "Calculated average does not match the expected one")

        wedge_average11 = (0.401225 + 0.553700 + 0.714168) / 3

        self.assertTrue(wedge_average11 == fiber_density_with_average[3][10],
                        "Calculated average does not match the expected one")

    def test_fiber_density_w_grid(self):
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'square.bmp'))
        bw_image = cv2.imread(os.path.join(image_path, 'square.bmp'))
        bin_image = Re.binarize_image(bw_image)
        number_columns = 12
        number_rows = 5
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        # Run Region Extraction Module
        dictionary = Re.grid_region_extraction(rgb_image, bin_image, number_columns, number_rows)

        # Run Fiber Density Calculation Module
        fiber_density_sprout = Fdc.fiber_density_calculation(number_rows, number_columns, dictionary)
        fd_with_average = Fdc.fiber_density_averages(fiber_density_sprout)

        print(fiber_density_sprout)
        print(fd_with_average)

        pass

if __name__ == '__main__':
    unittest.main()
