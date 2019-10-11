import cv2 as cv
import numpy as np
DEBUG = 0


def preprocessimage(imagename: str) -> object:

    def binarizeimage(sourceimage: object) -> object:
        gray_image = cv.cvtColor(sourceimage, cv.COLOR_BGR2GRAY)
        if DEBUG: cv.imwrite('grayscale_img.jpg', gray_image)

        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
        if DEBUG: cv.imwrite('blurred_img.jpg', blurred_image)

        ret, new_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        if DEBUG: cv.imwrite('binarized_bamboo.jpg', new_image)
        return new_image

    def imagecontours(sourceimage: object) -> object:
        contours, hierarchy = cv.findContours(sourceimage,
                                              cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        areas = [cv.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        x, y, w, h = cv.boundingRect(cnt)
        cv.rectangle(sourceimage, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if DEBUG: cv.imwrite('contoured_image.jpg', sourceimage)

        return sourceimage

    img = cv.imread('Images/bamboo.jpg')
    processed_image = binarizeimage(img)
    processed_image = imagecontours(processed_image)

    return processed_image


if __name__ == "__main__":

    processedimage = preprocessimage('Images/bamboo.jpg')
