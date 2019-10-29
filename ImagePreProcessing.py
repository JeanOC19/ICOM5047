import cv2 as cv
import os
import time
import numpy as np

DEBUG = 0
TESTING = 1
path = "Pre_Processing"


def save_dimensional_measurements(calculated_area: float, calculated_out_diam: float, calculated_in_diam: float,
                                  calculated_centroid: list, calculated_mom_of_x: float, calculated_mom_of_y: float,
                                  units: str):
    """
    Simulate sending the measurement data to the Data Management Module
    :param calculated_area: area of bamboo cross-section
    :param calculated_out_diam: outer diameter of the bamboo
    :param calculated_in_diam: inner diameter of the bamboo
    :param calculated_centroid: list containing the x and y coordinates of the centroid
    :param calculated_mom_of_x: moment of inertia with respect to the x axis
    :param calculated_mom_of_y: moment of inertia with respect to the y axis
    :param units: units of measurement used
    """
    print("Area: " + str(calculated_area) + " " + units + "2")
    print("Outer Diameter: " + str(calculated_out_diam) + " " + units)
    print("Inner Diameter: " + str(calculated_in_diam) + " " + units)
    print("Centroid: " + str(calculated_centroid[0]) + " " + units + ", " + str(calculated_centroid[1]) + " " + units)
    print("X-axis moment: " + str(calculated_mom_of_x) + " " + units + "4")
    print("Y-axis moment: " + str(calculated_mom_of_y) + " " + units + "4")


def save_diameter_measurements(outer_diameter_list: list, inner_diameter_list: list):
    """
    Simulate sending individual diameter measurements to the Data Management Module
    :param outer_diameter_list: list of measurements for the outer diameter
    :param inner_diameter_list: list of measurements for the inner diameter
    """
    print(outer_diameter_list)
    print(inner_diameter_list)


def update_progress_bar():
    """
    Simulate the process of updating the progress bar of the UI
    """
    print("Progress bar updated.")


def pre_process_image(image_name: str, num_of_measurements: int, image_dpi: int, units: str) -> object:
    def binarize_image(source_image: object) -> object:
        """Convert the input image into a binary image.
        """
        # Convert RGB image to grayscale
        gray_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
        if DEBUG:
            cv.imwrite(path + '/grayscale_img.jpg', gray_image)

        # Use Gaussian Blur to remove noise from the image
        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
        if DEBUG:
            cv.imwrite(path + '/blurred_img.jpg', blurred_image)

        # Calculate the global threshold value and binarize the image
        ret, new_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        if DEBUG:
            cv.imwrite(path + '/binarized_bamboo.jpg', new_image)
        return new_image

    def find_largest_contours(contour_list: list) -> object:

        largest_area = 0
        largest_contour = 100
        second_largest = 0
        second_largest_area = 0

        # Find largest and second largest contour in image (rings of the bamboo)
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
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        return cv.warpAffine(image, M, (nW, nH))

    def unit_converter():
        return lambda z: z / image_dpi * units_multiplier

    def image_contours(sourceimage: object, ) -> object:
        # Erode and dilate image to 
        eroded = cv.dilate(sourceimage, None, iterations=7)
        eroded = cv.erode(eroded, None, iterations=7)

        contours, hierarchy = cv.findContours(eroded, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
        largest_contour_index, second_largest_index = find_largest_contours(contours)

        contoured = img.copy()
        cv.drawContours(contoured, contours[largest_contour_index], -1, (0, 255, 0), 7)
        cv.drawContours(contoured, contours[second_largest_index], -1, (0, 255, 0), 7)
        cv.imwrite(path + '/contour_image.jpg', contoured)

        x, y, w, h = cv.boundingRect(contours[largest_contour_index])
        bounded_image = img[y:y + h, x:x + w]
        binarized_bounded_image = sourceimage[y:y + h, x:x + w]
        cv.imwrite(path + '/bounded_image.jpg', bounded_image)
        cv.imwrite(path + '/binarized_bounded_image.jpg', binarized_bounded_image)

        eroded = binarized_bounded_image
        eroded = cv.dilate(eroded, None, iterations=13)
        eroded = cv.erode(eroded, None, iterations=13)

        bounded_filled_image = eroded
        cv.imwrite(path + '/eroded_image.jpg', bounded_filled_image)

        x2, y2, w2, h2 = cv.boundingRect(contours[second_largest_index])
        outer_diameter_measurements = [w, h]
        inner_diameter_measurements = [w2, h2]
        pre_rotated_image = bounded_filled_image.copy()

        radius_steps = int(90 / (num_of_measurements / 2))

        # Make multiple inner and outer diameter measurements
        for angle in range(radius_steps, 90, radius_steps):
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

        output = cv.connectedComponentsWithStats(bounded_filled_image, 4, cv.CV_32S)
        meas_area = (output[2][1][4] / (image_dpi ** 2)) * (units_multiplier ** 2)

        meas_centroid = [0, 0]
        centroid_coordinates = (int(output[3][1][0]), int(output[3][1][1]))
        meas_centroid[0] = ((centroid_coordinates[0] / image_dpi) * units_multiplier)
        meas_centroid[1] = ((centroid_coordinates[1] / image_dpi) * units_multiplier)
        cv.circle(bounded_image, centroid_coordinates, 10, (0, 255, 255), 10)
        cv.imwrite(path + "/centroid.jpg", bounded_image)

        M = cv.moments(bounded_filled_image, binaryImage=True)

        x_moment = M['m02'] * ((units_multiplier / image_dpi) ** 4)
        y_moment = M['m20'] * ((units_multiplier / image_dpi) ** 4)

        return bounded_image, binarized_bounded_image, meas_area, meas_outer_diameter, meas_inner_diameter, \
            meas_centroid, x_moment, y_moment, outer_diameter_measurements, inner_diameter_measurements

    # Validate inputs
    assert type(num_of_measurements) is int, "Dimensional measurements number is not an integer."
    assert type(image_dpi) is int, "Image DPI is not an integer."
    assert type(units) is str, "Units of measurement is not a string."
    assert 400 >= num_of_measurements >= 4, "Number of dimensional measurements is not in allowed range."
    assert 2600 >= image_dpi >= 0, "Image DPI should be between 0 and 2600."
    assert units in ('cm', 'in', 'mm'), "Supported units are only inches(in), centimeters(cm), and milimeters(mm)"

    # Create folder for images
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

    img = cv.imread(image_name)

    # Binarize the input image
    try:
        processed_image = binarize_image(img)
    except:
        raise Exception("Unable to binarize input image.")

    # Find contours of the image and make dimensional measurements
    try:
        image, binarized_image, area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y, \
            outer_measurements, inner_measurements = image_contours(processed_image)
        save_dimensional_measurements(area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y, units)
        save_diameter_measurements(outer_measurements, inner_measurements)
    except:
        raise Exception("Unable to calculate dimensional measurements of bamboo")

    update_progress_bar()

    if TESTING:
        return image, binarized_image, area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y, \
            outer_measurements, inner_measurements
    else:
        return image, binarized_image


if __name__ == "__main__":
    startt = time.process_time()

    processed_image, image = pre_process_image('Images/R_0.0.0.jpg', 8, 1200, 'cm')

    print("Total time: " + str(time.process_time() - startt))
