import cv2 as cv
import os
import time
import numpy as np

# Global variables for testing purposes
TESTING = 0
outer_units = ""


def set_dimensional_measurements(measurements_list: list):
    """
    Simulate sending the measurement data to the Data Management Module
    :param measurements_list: list containing all the measurements made by the pre-processing module in the following
            order:  area, outer diameter, inner diameter, x coordinate of centroid, y coordinate of centroid,
                    X moment of inertia, y moment of inertia
    """
    print()
    print("Data Management module received:")
    print(measurements_list)
    print()
    if TESTING:
        print("Area: " + str(measurements_list[0]) + " " + outer_units + "2")
        print("Outer Diameter: " + str(measurements_list[1]) + " " + outer_units)
        print("Inner Diameter: " + str(measurements_list[2]) + " " + outer_units)
        print("Centroid: " + str(measurements_list[3]) + " " + outer_units + ", "
              + str(measurements_list[4]) + " " + outer_units)
        print("X-axis moment: " + str(measurements_list[5]) + " " + outer_units + "4")
        print("Y-axis moment: " + str(measurements_list[6]) + " " + outer_units + "4")
        print("Product of inertia: " + str(measurements_list[7]) + " " + outer_units + "4")


def set_diameters(diameter_list: list):
    """
    Simulate sending individual diameter measurements to the Data Management Module
    :param diameter_list: list with two columns, one for outer diameter measurements and one for inner diameter measurements.
    """
    print()
    print("Data Management module received:")
    print(diameter_list)
    print()


def pre_process_image(num_of_measurements: int, image_dpi: int, units: str, image_path: str = None,
                      enhanced_image: object = None):
    """
    Takes a bamboo image and binarizes it then bounds it and determines its area, inner and outer diameters, centroid coordinates, and moment of inertia with respect to the x and y axes
    :param num_of_measurements: number of measurements to use for determining average inner and outer diameters
    :param image_dpi: DPI of the input image
    :param units: units used for displaying measurements (cm, in, or mm)
    :param image_path: path of the input image to be used
    :param enhanced_image: data of the input image (for when image enhancement is used)
    :return: bounded input image and bounded binarized input image
    """

    def binarize_image(source_image: object) -> object:
        """
        Converts the input image into a binary image
        :param source_image: image to be binarized
        :return: binarized image data
        """
        # Convert RGB image to grayscale
        gray_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
        cv.imwrite(path + '/grayscale_image.jpg', gray_image)

        # Use Gaussian Blur to remove noise from the image
        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)

        # Calculate the global threshold value and binarize the image
        ret, new_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        cv.imwrite(path + '/binarized_image.jpg', new_image)

        return new_image

    def find_largest_contours(contour_list: list) -> object:

        largest_area = 0
        largest_contour = 100
        second_largest = 0
        second_largest_area = 0

        # Find largest and second largest contours in image (rings of the bamboo)
        for i in range(len(contour_list)):
            contour_area = cv.contourArea(contour_list[i])
            if contour_area > largest_area:
                largest_area = contour_area
                second_largest = largest_contour
                largest_contour = i
            elif contour_area > second_largest_area:
                second_largest_area = contour_area
                second_largest = i

        return largest_contour, second_largest

    def rotate_image(image, angle):
        """
        Function to rotate the input image by a specified angle
        :param image: input image to rotate
        :param angle: number of degrees the image will be rotated by
        :return: rotated input image
        """
        # determine center of the image
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # get the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then get the sine and cosine
        M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # Calculate bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        return cv.warpAffine(image, M, (nW, nH))

    def unit_converter():
        """
        Lambda function to convert values to corresponding units
        :return: lambda function
        """
        return lambda z: z / image_dpi * units_multiplier

    def image_contours(source_image: object):
        """
        Find the contours of the bamboo, bound the image and make all dimensional measurements
        :param source_image: binarized input image
        :return: bounded image, bounded binarized image, area, outer diameter, inner diameter,
                 centroid, x moment, y moment, inner diameter measurements, and outer diameter lists
        """
        # Erode and dilate image to 
        eroded = cv.dilate(source_image, None, iterations=7)
        eroded = cv.erode(eroded, None, iterations=7)

        # Find contours of the image and select those belonging to the bamboo
        contours, hierarchy = cv.findContours(eroded, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
        largest_contour_index, second_largest_index = find_largest_contours(contours)

        # Draw bamboo contours on the image and save the new image
        contoured = img.copy()
        cv.drawContours(contoured, contours[largest_contour_index], -1, (0, 255, 0), 7)
        cv.drawContours(contoured, contours[second_largest_index], -1, (0, 255, 0), 7)
        cv.imwrite(path + '/contour_image.jpg', contoured)

        # Find the bounding box of the largest contour and crop both the input and binarized image
        x, y, w, h = cv.boundingRect(contours[largest_contour_index])
        bounded_image = img[y:y + h, x:x + w]
        binarized_bounded_image = source_image[y:y + h, x:x + w]
        cv.imwrite(path + '/bounded_image.jpg', bounded_image)
        cv.imwrite(path + '/binarized_bounded_image.jpg', binarized_bounded_image)

        # Dilate and erode the bounded image to fill the fibers. Then save the image
        eroded = binarized_bounded_image
        eroded = cv.dilate(eroded, None, iterations=13)
        eroded = cv.erode(eroded, None, iterations=13)
        bounded_filled_image = eroded
        cv.imwrite(path + '/filled_image.jpg', bounded_filled_image)

        # Find the bounding box of the inner bamboo ring and store the height and width
        x2, y2, w2, h2 = cv.boundingRect(contours[second_largest_index])
        outer_diameter_measurements = [w, h]
        inner_diameter_measurements = [w2, h2]
        pre_rotated_image = bounded_filled_image.copy()

        # Calculate the degrees between each measurement
        radius_steps = int(360 / ((num_of_measurements - 2) / 2))

        # Make multiple inner and outer diameter measurements
        for angle in range(radius_steps, int(radius_steps * (num_of_measurements / 2)), radius_steps):
            # Rotate image
            rotated_image = rotate_image(pre_rotated_image, angle)
            # Find contours of rotated image and find inner and outer ring
            new_contours, new_hierarchy = cv.findContours(rotated_image, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
            largest_contour_index, second_largest_index = find_largest_contours(new_contours)

            # Find bounding box of both rings, take height and width as new measurements
            x2, y2, w2, h2 = cv.boundingRect(new_contours[largest_contour_index])
            outer_diameter_measurements.append(w2)
            outer_diameter_measurements.append(h2)
            x2, y2, w2, h2 = cv.boundingRect(new_contours[second_largest_index])
            inner_diameter_measurements.append(w2)
            inner_diameter_measurements.append(h2)

        # Convert the radial measurements to user input units
        outer_diameter_measurements = list(map(unit_converter(), outer_diameter_measurements))
        inner_diameter_measurements = list(map(unit_converter(), inner_diameter_measurements))

        # Calculate the average inner and outer diameters
        meas_outer_diameter = sum(outer_diameter_measurements) / len(outer_diameter_measurements)
        meas_inner_diameter = sum(inner_diameter_measurements) / len(inner_diameter_measurements)

        # Find the statistics of the filled ring and convert the area to specified units
        output = cv.connectedComponentsWithStats(bounded_filled_image, 4, cv.CV_32S)
        meas_area = (output[2][1][4] / (image_dpi ** 2)) * (units_multiplier ** 2)

        # Find the coordinates of the centroid and convert them to the specified units
        meas_centroid = [0, 0]
        M = cv.moments(bounded_filled_image, binaryImage=True)
        centroid_coordinates = (M['m10'] / M['m00'], M['m01'] / M['m00'])
        meas_centroid[0] = centroid_coordinates[0] * units_multiplier / image_dpi
        meas_centroid[1] = centroid_coordinates[1] * units_multiplier / image_dpi

        # Draw the centroid on the image and save it
        cv.circle(bounded_image, (int(centroid_coordinates[0]), int(centroid_coordinates[1])), 10, (0, 255, 255), 10)
        cv.imwrite(path + "/centroid.jpg", bounded_image)

        # Calculate the moments of the image and obtain the second moments to get the moments of inertia
        x_moment = (M['m02']) * ((units_multiplier / image_dpi) ** 4)
        y_moment = (M['m20']) * ((units_multiplier / image_dpi) ** 4)
        moment_product = (M['m11']) * ((units_multiplier / image_dpi) ** 4)

        return bounded_image, binarized_bounded_image, [meas_area, meas_outer_diameter, meas_inner_diameter,
                                                        meas_centroid[0], meas_centroid[1], x_moment, y_moment,
                                                        moment_product], [outer_diameter_measurements,
                                                                          inner_diameter_measurements]

    # Validate inputs
    assert image_path is not None, "Image path must be given as input."
    assert type(num_of_measurements) is int, "Dimensional measurements number is not an integer."
    assert type(image_dpi) is int, "Image DPI is not an integer."
    assert type(units) is str, "Units of measurement is not a string."
    assert 400 >= num_of_measurements >= 12, "Number of dimensional measurements is not in allowed range."
    assert 4800 >= image_dpi >= 25, "Image DPI should be between 25 and 4800."
    assert units in ('cm', 'in', 'mm'), "Supported units are only inches(in), centimeters(cm), and milimeters(mm)"
    assert os.path.exists(image_path), "Input image was not found."

    path = "Pre_Processing"
    global TESTING
    if TESTING:
        global outer_units
        outer_units = units

    # Create folder for images if it does not exist
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            raise Exception("Unable to create Pre-Processing sub-directory")

    # Dictionary to store the conversion value of each unit of measurement
    units_dict = {'cm': 2.54,
                  'mm': 25.4,
                  'in': 1}
    units_multiplier = units_dict[units]

    # Check if input is the image path or the image data
    if enhanced_image is None:
        try:
            img = cv.imread(image_path)
        except Exception:
            raise Exception("Unable to open input image")
    else:
        img = enhanced_image

    # Binarize the input image
    try:
        binarized_image = binarize_image(img)
    except:
        raise Exception("Unable to binarize input image.")

    try:
        # Find contours of the image and make dimensional measurements
        image, binarized_image, measurements_list, diameters_list = image_contours(binarized_image)
        set_dimensional_measurements(measurements_list)
        set_diameters(diameters_list)
    except:
        raise Exception("Unable to calculate dimensional measurements of bamboo")

    # If user is testing module, send all the parameters
    if TESTING:
        return binarized_image, image, measurements_list[0], measurements_list[1], measurements_list[2], \
               measurements_list[3], measurements_list[4], measurements_list[5], measurements_list[6], \
               measurements_list[7], diameters_list[0], diameters_list[1]
    else:
        return binarized_image, image


if __name__ == "__main__":
    startt = time.process_time()
    bounded_binarized_image, bounded_input_image = pre_process_image(12, 1200, 'cm', image_path='Images/R_0.0.0.jpg')
    print("Total time: " + str(time.process_time() - startt))
