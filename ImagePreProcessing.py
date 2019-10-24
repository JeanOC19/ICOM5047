import cv2 as cv
import time
import numpy as np

DEBUG = 0


def pre_process_image(image_name: str, num_of_measurements: int, image_dpi: int, units: str) -> object:

    def binarize_image(source_image: object) -> object:
        gray_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
        if DEBUG: cv.imwrite('grayscale_img.jpg', gray_image)

        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
        if DEBUG: cv.imwrite('blurred_img.jpg', blurred_image)

        ret, new_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        if DEBUG: cv.imwrite('binarized_bamboo.jpg', new_image)
        return new_image

    def findlargestcontours(contour_list):

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

        eroded = cv.dilate(sourceimage, None, iterations=7)
        eroded = cv.erode(eroded, None, iterations=7)

        contours, hierarchy = cv.findContours(eroded, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
        largest_contour_index, second_largest_index = findlargestcontours(contours)

        # M = cv.moments(contours[largest_contour_index])
        # x_moment = (M['m02']/image_dpi ** 4) * (units_multiplier ** 4)
        # y_moment = (M['m20']/image_dpi ** 4) * (units_multiplier ** 4)

        contoured = img.copy()
        cv.drawContours(contoured, contours[largest_contour_index], -1, (0, 255, 0), 7)
        cv.drawContours(contoured, contours[second_largest_index], -1, (0, 255, 0), 7)
        cv.imwrite('contour_image.jpg', contoured)

        x, y, w, h = cv.boundingRect(contours[largest_contour_index])
        bounded_image = img[y:y + h, x:x + w]
        binarized_bounded_image = sourceimage[y:y + h, x:x + w]
        cv.imwrite('bounded_image.jpg', bounded_image)
        cv.imwrite('binarized_bounded_image.jpg', binarized_bounded_image)

        eroded = binarized_bounded_image
        eroded = cv.dilate(eroded, None, iterations=13)
        eroded = cv.erode(eroded, None, iterations=13)

        bounded_filled_image = eroded
        cv.imwrite('eroded_image.jpg', bounded_filled_image)

        x2, y2, w2, h2 = cv.boundingRect(contours[second_largest_index])
        outer_diameter_measurements = [w, h]
        inner_diameter_measurements = [w2, h2]
        pre_rotated_image = bounded_filled_image.copy()

        # Make multiple inner and outer diameter measurements
        for angle in range(0, 360, int(360/(num_of_measurements/2))):
            # Rotate image
            rotated_image = rotate_image(pre_rotated_image, angle)
            # Find contours of rotated image and find inner and outer ring
            new_contours, new_hierarchy = cv.findContours(rotated_image, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
            largest_contour_index, second_largest_index = findlargestcontours(new_contours)

            # Find bounding box of both rings, take height and width as new measurements
            x2, y2, w2, h2 = cv.boundingRect(new_contours[largest_contour_index])
            outer_diameter_measurements.append(w2)
            outer_diameter_measurements.append(h2)
            x2, y2, w2, h2 = cv.boundingRect(new_contours[second_largest_index])
            inner_diameter_measurements.append(w2)
            inner_diameter_measurements.append(h2)

        outer_diameter_measurements = list(map(unit_converter(), outer_diameter_measurements))
        inner_diameter_measurements = list(map(unit_converter(), inner_diameter_measurements))

        meas_outer_diameter = sum(outer_diameter_measurements)/len(outer_diameter_measurements)
        meas_inner_diameter = sum(inner_diameter_measurements) / len(inner_diameter_measurements)

        output = cv.connectedComponentsWithStats(bounded_filled_image, 4, cv.CV_32S)
        meas_area = (output[2][1][4] / (image_dpi ** 2)) * (units_multiplier ** 2)

        meas_centroid = [0, 0]
        centroid_coordinates = (int(output[3][1][0]), int(output[3][1][1]))
        meas_centroid[0] = ((centroid_coordinates[0] / image_dpi) * units_multiplier)
        meas_centroid[1] = ((centroid_coordinates[1] / image_dpi) * units_multiplier)
        cv.circle(bounded_image, centroid_coordinates, 10, (0, 255, 255), 10)
        cv.imwrite("centroid.jpg", bounded_image)

        M = cv.moments(bounded_filled_image, binaryImage=True)

        x_moment = M['m02'] * ((units_multiplier/image_dpi) ** 4)
        y_moment = M['m20'] * ((units_multiplier/image_dpi) ** 4)

        return bounded_image, binarized_bounded_image, meas_area, meas_outer_diameter, meas_inner_diameter, meas_centroid, x_moment, y_moment

    # Validate inputs
    assert type(num_of_measurements) is int, "Dimensional measurements number is not an integer."
    assert type(image_dpi) is int, "Image DPI is not an integer."
    assert type(units) is str, "Units of measurement is not a string."
    assert 400 >= num_of_measurements >= 4, "Number of dimensional measurements is not in allowed range."
    assert units in ('cm', 'in', 'mm'), "Supported units are only inches(in), centimeters(cm), and milimeters(mm)"

    units_dict = {'cm': 2.54,
                  'mm': 25.4,
                  'in': 1}
    units_multiplier = units_dict[units]

    img = cv.imread(image_name)
    processed_image = binarize_image(img)
    image, binarized_image, area, outer_diameter, inner_diameter, centroid, moment_of_x, moment_of_y = image_contours(
        processed_image)

    print("Area: " + str(area) + " " + units + "2")
    print("Outer Diameter: " + str(outer_diameter) + " " + units)
    print("Inner Diameter: " + str(inner_diameter) + " " + units)
    print("Centroid: " + str(centroid[0]) + " " + units + ", " + str(centroid[1]) + " " + units)
    print("X-axis moment: " + str(moment_of_x) + " " + units + "4")
    print("Y-axis moment: " + str(moment_of_y) + " " + units + "4")

    return image, binarized_image


if __name__ == "__main__":
    startt = time.process_time()
    processedimage = pre_process_image('Images/R_1.1.1.jpg', 4, 1800, 'in')
    print("Total time: " + str(time.process_time() - startt))
