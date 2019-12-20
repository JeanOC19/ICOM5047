import unittest
import Region_Extraction as re
import cv2
import os
import time


class MyTestCase(unittest.TestCase):

    def test_measurements(self):

        print("Test Measurements")

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = re.binarize_image(bw_image)

        c_x, c_y = re.get_centroid(bin_image)
        c_x_cm = (c_x * 2.54) / 1200  # (center_x * unit_multiplier(cm))/ image_dpi
        c_y_cm = (c_y * 2.54) / 1200  # (center_y * unit_multiplier(cm))/ image_dpi

        self.assertLessEqual(calculate_error(c_x_cm, 3.2406), 3.5, "Centroid X axis has more than 3.5% of error")
        self.assertLessEqual(calculate_error(c_y_cm, 3.4100), 3.5, "Centroid Y axis has more than 3.5% of error")

    def test_input_validation(self):
        print("Testing validation of input parameters")
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = re.binarize_image(bw_image)

        self.assertRaises(AssertionError, re.region_extraction, 0, bin_image, 12, 3)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, 0, 12, 3)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 12.5, 3)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 12, 3.5)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 12, -1)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 12, 30)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 4, 3)
        self.assertRaises(AssertionError, re.region_extraction, rgb_image, bin_image, 500, 3)

    def test_region_storage(self):
        print("Testing region storage")

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = re.binarize_image(bw_image)
        number_wedges = 12
        number_rings = 3
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        regions_path = os.path.join(int_path, 'Regions')
        os.chdir(int_path)

        # Run Region Extraction
        re.region_extraction(rgb_image, bin_image, number_wedges, number_rings)

        # Check if 'regions' directory is created in intermediate path
        self.assertTrue(os.path.exists(regions_path), "'Regions' directory does not exist in intermediate path")

        # Check if all files are being created in the 'regions' directory.
        expected_regions = calculate_num_of_expected_regions(number_wedges, number_rings)
        num_files_in_dir = len([f for f in os.listdir(regions_path) if os.path.isfile(os.path.join(regions_path, f))])
        self.assertTrue(expected_regions == num_files_in_dir,
                        "Expected Regions and Number of Files in 'regions' directory do not match")

        # Check if files are named Rn_Wm where n is a number and m is another number
        for f in os.listdir(regions_path):
            self.assertTrue(str(f).find("R") != -1, "%s does not contain R in its name" % f)
            self.assertTrue(str(f).find("W") != -1, "%s does not contain W in its name" % f)

    def test_execution_time(self):
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = re.binarize_image(bw_image)
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        start_time = time.time()
        re.region_extraction(rgb_image, bin_image, 12, 3)
        execution_time = (time.time() - start_time)
        print("--- %s seconds ---" % execution_time)

        self.assertLessEqual(execution_time, (60 * .5), "Execution time takes more than 50% of a minute")

    def test_edges(self):
        print("Test all possibilities")

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'control_rgb.jpg'))
        bw_image = cv2.imread(os.path.join(image_path, 'control.png'))
        bin_image = re.binarize_image(bw_image)
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        try:
            re.region_extraction(rgb_image, bin_image, 12, 1)
        except Exception:
            raise Exception("Failed test at: Number of Wedges(%d), Number of Rings(%d)" % (12, 1))

        try:
            re.region_extraction(rgb_image, bin_image, 400, 1)
        except Exception:
            raise Exception("Failed test at: Number of Wedges(%d), Number of Rings(%d)" % (400, 1))

        try:
            re.region_extraction(rgb_image, bin_image, 12, 25)
        except Exception:
            raise Exception("Failed test at: Number of Wedges(%d), Number of Rings(%d)" % (12, 25))

        try:
            re.region_extraction(rgb_image, bin_image, 400, 25)
        except Exception:
            raise Exception("Failed test at: Number of Wedges(%d), Number of Rings(%d)" % (12, 25))

    def test_grid_region_extraction(self):
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        rgb_image = cv2.imread(os.path.join(image_path, 'square.bmp'))
        bw_image = cv2.imread(os.path.join(image_path, 'square.bmp'))
        bin_image = re.binarize_image(bw_image)
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        try:
            re.grid_region_extraction(rgb_image, bin_image, 12, 12)
        except Exception:
            raise Exception("Test Failed")


def calculate_error(measure, actual):
    return (abs(actual - measure)/actual) * 100


def calculate_num_of_expected_regions(num_wedges, num_rings):
    return num_wedges * num_rings


if __name__ == '__main__':
    unittest.main()
