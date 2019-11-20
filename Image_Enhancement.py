import cv2
import numpy as np
import os
import shutil


def adjust_gamma(image, gamma=1.0):
    """
    Adjust an input image gamma.
    :param image: Input image
    :param gamma: Gamma value that will be applied to the image
    :return: Image with gamma correction
    """

    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def store_image(img):
    """
    Store a given image on the 'enhanced_image' directory.
    :param img: Input image
    :return: None
    """
    """Store a given  image in a specified directory"""

    img_name = "enhanced_image.jpg"
    img_enhacement_path = 'Image_enhancement'
    intermediate_path = os.getcwd()
    full_path = os.path.join(intermediate_path, img_enhacement_path)

    # Check if path exists, if not then create the path
    if not os.path.exists(full_path):
        print("Didn't found directory: %s. Proceeding to create directory." % full_path)
        try:
            os.mkdir(img_enhacement_path)
        except OSError:
            print("Creation of the directory %s failed" % img_enhacement_path)
        else:
            print("Successfully created the directory: %s " % img_enhacement_path)
    # Check if path is empty , if not then delete contents
    elif os.listdir(full_path):
        print("Found directory: %s with content. Proceeding to delete contents" % full_path)
        try:
            shutil.rmtree(full_path)
            os.mkdir(img_enhacement_path)
        except OSError:
            print("Could not delete contents of directory: %s" % full_path)
        else:
            print("Successfully deleted contents of the directory: %s " % full_path)

    # Store region image
    try:
        cv2.imwrite(os.path.join(full_path, str(img_name)), img)
    except OSError:
        print("Storage of %s failed on path" % img_name % img_enhacement_path)
    else:
        print("Stored: ", os.path.join(full_path, str(img_name)))


def image_enhancement(image_path: str):
    """
    Given an input image path, load the image and enhance the dark regions of the bibers.
    :param image_path: Path where the image is located.
    :return: Enhanced image
    """

    # Validate Input
    assert type(image_path) is not None, "Image path cannot be none"
    assert type(image_path) is str, "Image path input must be a string"

    # Load image
    try:
        image = cv2.imread(image_path)
    except Exception:
        raise Exception("Unable to open file: %s" % image_path)

    # Apply gamma correction to lower the brightness of the image
    low_bright_img = adjust_gamma(image, .25)

    # Change Image Color Encoding
    yuv_img = cv2.cvtColor(low_bright_img, cv2.COLOR_BGR2YUV)

    # Equalize the histogram of the Y channel
    yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])

    # convert the YUV image back to RGB format
    bgr_img = cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    # Apply gamma correction to raise the brightness of the image
    enhanced_img = adjust_gamma(bgr_img, 1.0)

    # Store image on file system
    store_image(enhanced_img)

    return enhanced_img


if __name__ == "__main__":

    os.chdir("C:/Users/Caloj/Desktop/Sprout_Images")

    img_path = "C:/Users/Caloj/PycharmProjects/ICOM5047/bamboo.jpg"

    Enhanced_Image = image_enhancement(img_path)
