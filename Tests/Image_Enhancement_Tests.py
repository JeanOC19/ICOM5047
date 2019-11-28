import unittest
import Image_Enhancement as ie
import os
import cv2


class MyTestCase(unittest.TestCase):

    def test_visual_1(self):
        print("Visual Test 1")
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path = os.path.join(image_path, 'bamboo.jpg')
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        orig_image = cv2.imread(img_path)
        show_image(resize_image(orig_image))

        # Run Image_Enhancement
        enhanced_image = ie.image_enhancement(img_path)
        show_image(resize_image(enhanced_image))

    def test_visual_3(self):
        print("Visual Test 1")
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path = os.path.join(image_path, '1.5.05.tiff')
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        orig_image = cv2.imread(img_path)
        show_image(resize_image(orig_image))

        # Run Image_Enhancement
        enhanced_image = ie.image_enhancement(img_path)
        show_image(resize_image(enhanced_image))

    def test_visual_4(self):
        print("Visual Test 1")
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path = os.path.join(image_path, '5.1.10.tiff')
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        orig_image = cv2.imread(img_path)
        show_image(resize_image(orig_image))

        # Run Image_Enhancement
        enhanced_image = ie.image_enhancement(img_path)
        show_image(resize_image(enhanced_image))

    def test_visual_5(self):
        print("Visual Test 1")
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path = os.path.join(image_path, 'R_1.1.1.jpg')
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        os.chdir(int_path)

        print(img_path)

        orig_image = cv2.imread(img_path)
        show_image(resize_image(orig_image))

        # Run Image_Enhancement
        enhanced_image = ie.image_enhancement(img_path)
        show_image(resize_image(enhanced_image))

    def test_input_validation(self):
        print("Testing Input Validation")

        img_path1 = 123
        img_path2 = None
        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path3 = cv2.imread(os.path.join(image_path, 'non_existing_photo.jpg'))
        img_path4 = 'image.pdf'

        self.assertRaises(AssertionError, ie.image_enhancement, img_path1)
        self.assertRaises(AssertionError, ie.image_enhancement, img_path2)
        self.assertRaises(AssertionError, ie.image_enhancement, img_path3)
        self.assertRaises(AssertionError, ie.image_enhancement, img_path4)

    def test_image_storage(self):
        print("Testing image storage")

        image_path = os.path.join(os.path.dirname(os.getcwd()), 'Images')
        img_path = os.path.join(image_path, 'bamboo.jpg')
        int_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sprout_Images")
        img_enhancement_path = os.path.join(int_path, 'image_enhancement')
        os.chdir(int_path)

        # Run Image_Enhancement
        ie.image_enhancement(img_path)

        # Check if 'image_enhancement' directory is created in intermediate path
        self.assertTrue(os.path.exists(img_enhancement_path),
                        "'image_enhancement' directory does not exist in intermediate path")

        # Check that 'image_enhancement' contains only one file
        num_files_in_dir = len([f for f in os.listdir(img_enhancement_path)
                                if os.path.isfile(os.path.join(img_enhancement_path, f))])
        self.assertTrue(num_files_in_dir == 1,
                        "File in 'image_enhancement' directory do not match")

        # Check if file created in 'image_enhancement' directory is named correctly
        for f in os.listdir(img_enhancement_path):
            self.assertEqual(str(f), "enhanced_image.jpg", "%s not not found" % f)


def resize_image(image):
    """
    Resize an image
    :param image: Input image
    :return: Resized Image
    """

    img = image.copy()

    # Obtain parameters for scaling
    height, width = img.shape[0], img.shape[1]
    imgScale = 600 / width
    newX, newY = img.shape[1] * imgScale, img.shape[0] * imgScale

    # Rescale the image
    return cv2.resize(img, (int(newX), int(newY)))


def show_image(img):
    """
    Show an input image on screen.
    :param img: Input image
    :return: None
    """
    cv2.imshow('Image', img)
    cv2.waitKey(0)


if __name__ == '__main__':
    unittest.main()
