import unittest
import Image_Enhancement
import ImagePreProcessing
import os


class MyTestCase(unittest.TestCase):
    def test_with_enhancement(self):
        img_path = '../Images/R_0.0.0.jpg'
        enhanced_image = Image_Enhancement.image_enhancement(img_path)
        ImagePreProcessing.pre_process_image(12, 1200, 'cm', img_path, enhanced_image)

        self.assertTrue(os.path.exists('Image_Enhancement'))
        self.assertTrue(os.path.exists('Pre_Processing'))
        self.assertTrue(os.path.exists('Image_Enhancement/enhanced_image.jpg'))

    def test_without_enhancement(self):
        img_path = '../Images/R_0.0.0.jpg'
        ImagePreProcessing.pre_process_image(12, 1200, 'cm', img_path, None)

        self.assertTrue(os.path.exists('Image_Enhancement'))
        self.assertTrue(os.path.exists('Pre_Processing'))
        self.assertTrue(os.path.exists('Image_Enhancement/enhanced_image.jpg'))


if __name__ == '__main__':
    unittest.main()
