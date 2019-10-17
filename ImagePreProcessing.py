import cv2 as cv
import time
import numpy as np

DEBUG = 0


def preprocess_image(image_name: str, num_of_rings: int, num_of_wedges: int, num_of_measurements: int,
                     image_dpi: int, units: str) -> object:
    def binarizeimage(source_image: object) -> object:
        gray_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
        if DEBUG: cv.imwrite('grayscale_img.jpg', gray_image)

        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
        if DEBUG: cv.imwrite('blurred_img.jpg', blurred_image)

        ret, new_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        if DEBUG: cv.imwrite('binarized_bamboo.jpg', new_image)
        return new_image

    def imagecontours(sourceimage: object) -> object:
        eroded = cv.dilate(sourceimage, None, iterations=10)
        eroded = cv.erode(eroded, None, iterations=9)

        contours, hierarchy = cv.findContours(eroded, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
        largest_area = 0
        largest_contour_index = 100
        second_largest_index = 0
        second_largest_area = 0

        # Find largest and second largest contour in image (rings of the bamboo)
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            if area > largest_area:
                largest_area = area
                second_largest_index = largest_contour_index
                largest_contour_index = i
            elif area > second_largest_area:
                second_largest_area = area
                second_largest_index = i

        contoured = img.copy()
        cv.drawContours(contoured, contours[largest_contour_index], -1, (0, 255, 0), 7)
        cv.drawContours(contoured, contours[second_largest_index], -1, (0, 255, 0), 7)
        cv.imwrite('contour_image.jpg', contoured)

        x, y, w, h = cv.boundingRect(contours[largest_contour_index])
        # cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 0)
        bounded_image = img[y:y + h, x:x + w]
        binarized_bounded_image = sourceimage[y:y + h, x:x + w]
        cv.imwrite('bounded_image.jpg', bounded_image)
        cv.imwrite('binarized_bounded_image.jpg', binarized_bounded_image)

        bounded_filled_image = eroded[y:y + h, x:x + w]
        output = cv.connectedComponentsWithStats(eroded, 4, cv.CV_32S)

        cv.imwrite('eroded_image.jpg', bounded_filled_image)

        meas_area = output[2][0][4] / (image_dpi * image_dpi) * 2.54
        meas_outer_diameter = ((w + h) / 2) / image_dpi * 2.54
        x, y, w, h = cv.boundingRect(contours[second_largest_index])
        meas_inner_diameter = ((w + h) / 2) / image_dpi * 2.54
        meas_centroid = output[3][0]
        mu = cv.moments(contours[second_largest_index], binaryImage=False)
        meas_centroid[0] = (int(mu['m10']/ mu['m00']) / (image_dpi*2)) * 2.54
        meas_centroid[1] = (int(mu['m01'] / mu['m00']) / (image_dpi*2)) * 2.54
        cv.circle(bounded_image, (int(mu['m10']/ mu['m00']/1.5), int(mu['m01'] / mu['m00']/1.5)), 10, (0,255,255), 10)
        cv.imwrite("centroid.jpg", bounded_image)
        # meas_centroid[0] = (meas_centroid[0] / image_dpi) * 2.54
        # meas_centroid[1] = (meas_centroid[1] / image_dpi) * 2.54
        meas_moments_of_inertia = 0.5 * (((meas_inner_diameter / 2) ** 2) + (meas_outer_diameter / 2) ** 2)

        return bounded_image, binarized_bounded_image, meas_area, meas_outer_diameter, meas_inner_diameter, meas_centroid, meas_moments_of_inertia

    img = cv.imread(image_name)
    processed_image = binarizeimage(img)
    image, binarized_image, area, outer_diameter, inner_diameter, centroid, moments_of_inertia = imagecontours(
        processed_image)

    print("Area: " + str(area) + " cm2")
    print("Outer Diameter: " + str(outer_diameter) + " cm")
    print("Inner Diameter: " + str(inner_diameter) + " cm")
    print("Centroid: " + str(centroid[0]) + " cm, " + str(centroid[1]) + " cm")
    print("Moments of Inertia: " + str(moments_of_inertia) + " cm4")
    return image, binarized_image


if __name__ == "__main__":
    startt = time.process_time()
    processedimage = preprocess_image('Images/bamboo.jpg', 3, 12, 12, 1200, 'cm')
    print("Total time: " + str(time.process_time() - startt))
