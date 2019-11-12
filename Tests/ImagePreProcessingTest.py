import unittest
import os
import ImagePreProcessing
import Image_Enhancement


class MyTestCase(unittest.TestCase):
    def test_dimensional_measurements_1(self):
        print("Testing measurements with sample 0.0.0")
        ImagePreProcessing.TESTING = 1
        new_img = Image_Enhancement.image_enhancement('../Images/R_0.0.0.jpg')

        image, binarized_image, area, outer_diameter, inner_diameter, centroid_x, centroid_y, moment_of_x, moment_of_y,\
            moment_product, outer_measurements, inner_measurements = \
            ImagePreProcessing.pre_process_image(16, 1200, 'cm', image_path='../Images/R_0.0.0.jpg', enhanced_image= new_img)
        # Compare measurements with actual values
        self.assertLessEqual(calculate_error(area, 16.2273), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(outer_diameter, 6.6696), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(inner_diameter, 4.8683), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_x, 3.2406), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_y, 3.4100), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_x, 24.9764), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_y, 34.5381), 3.5, "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_product, -1.2249), 3.5, "Product of inertia calculation has more than 3.5% of error")

    def test_dimensional_measurements_2(self):
        print("Testing measurements with sample 1.1.1")
        ImagePreProcessing.TESTING = 1
        image, binarized_image, area, outer_diameter, inner_diameter, centroid_x, centroid_y, moment_of_x, moment_of_y, \
        moment_product, outer_measurements, inner_measurements = \
            ImagePreProcessing.pre_process_image(16, 1800, 'in', image_path='../Images/R_1.1.1.jpg')

        # Compare measurements with actual values
        self.assertLessEqual(calculate_error(area, 3.9020), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(outer_diameter, 2.9550), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(inner_diameter, 1.9560), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_x, 1.5011), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_y, 1.4572), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_x, 2.3856), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_y, 2.2770), 3.5, "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_product, 0.13438), 3.5,
                             "Product of inertia calculation has more than 3.5% of error")

    def test_dimensional_measurements_3(self):
        print("Testing measurements with sample 1.1.1")
        ImagePreProcessing.TESTING = 1
        new_img = Image_Enhancement.image_enhancement('../Images/1200dpi.jpg')

        image, binarized_image, area, outer_diameter, inner_diameter, centroid_x, centroid_y, moment_of_x, moment_of_y, \
        moment_product, outer_measurements, inner_measurements = \
            ImagePreProcessing.pre_process_image(16, 1200, 'cm', image_path='../Images/1200dpi.jpg', enhanced_image= new_img)

        # Compare measurements with actual values
        self.assertLessEqual(calculate_error(area, 10.8798), 3.5, "Area calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(outer_diameter, 6.3172), 3.5, "Inner diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(inner_diameter, 5.1043), 3.5, "Outer diam. has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_x, 3.1533), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(centroid_y, 3.1467), 3.5, "Centroid Y axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_x, 31.7354), 3.5, "X-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_of_y, 34.4873), 3.5, "Y-axis moment calculation has more than 3.5% of error")
        self.assertLessEqual(calculate_error(moment_product, 0.74789), 3.5,
                             "Product of inertia calculation has more than 3.5% of error")

    def test_file_creation(self):
        print("Testing file creation")

        # View if all files are being created in the respective directory
        ImagePreProcessing.pre_process_image(16, 1200, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertTrue(os.path.exists('Pre_Processing/binarized_image.jpg'), "Binarized image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/grayscale_image.jpg'), "Grayscale image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/binarized_bounded_image.jpg'), "Binarized bounded image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/bounded_image.jpg'), "Bounded input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/centroid.jpg'), "Centroid image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/contour_image.jpg'), "Contoured input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/filled_image.jpg'), "Filled image was not saved")

    def test_input_validation(self):
        print("Testing input parameter validation")

        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 11, 1200, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 16, 24, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 16, 1200, 'm', image_path='../Images/R_0.0.0.jpg')
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 16, 1200, 'cm', image_path=None, enhanced_image=None)
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 401, 1200, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 16, 4801, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertRaises(AssertionError,
                          ImagePreProcessing.pre_process_image, 16, 4800, 'cm', image_path='Non_existing.jpg')

    def test_edge_cases(self):
        print("Testing file creation")

        # View if all files are being created in the respective directory
        ImagePreProcessing.pre_process_image(12, 4800, 'cm', image_path='../Images/4800dpi.tif')
        self.assertTrue(os.path.exists('Pre_Processing/binarized_image.jpg'), "Binarized image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/grayscale_image.jpg'), "Grayscale image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/binarized_bounded_image.jpg'), "Binarized bounded image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/bounded_image.jpg'), "Bounded input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/centroid.jpg'), "Centroid image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/contour_image.jpg'), "Contoured input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/filled_image.jpg'), "Filled image was not saved")

        ImagePreProcessing.pre_process_image(400, 1200, 'cm', image_path='../Images/R_0.0.0.jpg')
        self.assertTrue(os.path.exists('Pre_Processing/binarized_image.jpg'), "Binarized image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/grayscale_image.jpg'), "Grayscale image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/binarized_bounded_image.jpg'), "Binarized bounded image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/bounded_image.jpg'), "Bounded input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/centroid.jpg'), "Centroid image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/contour_image.jpg'), "Contoured input image was not saved")
        self.assertTrue(os.path.exists('Pre_Processing/filled_image.jpg'), "Filled image was not saved")


def calculate_error(measure, actual):
    return (abs(actual - measure)/actual) * 100


if __name__ == '__main__':
    unittest.main()
