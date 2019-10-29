import unittest
import ImagePreProcessing


class MyTestCase(unittest.TestCase):
    def test_dimensional_measurements_1(self):
        print("Testing measurements with sample 0.0.0")
        image, binarized_image, area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y, \
            outer_measurements, inner_measurements = \
            ImagePreProcessing.pre_process_image('../Images/R_0.0.0.jpg', 8, 1200, 'cm')

        # Compare measurements with actual values
        self.assertLessEqual(calculate_error(area, 16.2273), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(outer_diameter, 6.6696), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(inner_diameter, 4.8683), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid[0], 3.2443), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid[1], 3.4131), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_y, 236.1723), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_x, 261.6978), 3.5, "Y-axis moment calculation has more than 3.5% of error")

    def test_dimensional_measurements_2(self):
        print("Testing measurements with sample 1.1.1")
        image, binarized_image, area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y, \
            outer_measurements, inner_measurements = \
            ImagePreProcessing.pre_process_image('../Images/R_1.1.1.jpg', 8, 1800, 'in')

        # Compare measurements with actual values
        self.assertLessEqual(calculate_error(area, 3.902), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(outer_diameter, 2.955), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(inner_diameter, 1.956), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid[0], 1.5021), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid[1], 1.4578), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_y, 11.9410), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_x, 11.2602), 3.5, "Y-axis moment calculation has more than 3.5% of error")

def calculate_error(measure, actual):
    return (abs(actual - measure)/actual) * 100


if __name__ == '__main__':
    unittest.main()
