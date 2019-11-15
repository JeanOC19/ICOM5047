import cv2
import numpy as np
import math
import os

# List generated after separating image into regions
regions_list = dict()


def resize_image(img, scale):
    """
    Resize an image
    :param img: Input image
    :param scale:
    :return:
    """

    # Obtain parameters for scaling
    height, width = img.shape[0], img.shape[1]
    img_scale = scale / width
    new_x, new_y = img.shape[1] * img_scale, img.shape[0] * img_scale

    # Rescale the image
    return cv2.resize(img, (int(new_x), int(new_y))), img_scale


def enlarge_image(img, scale):
    """
    Resize an image
    :param img: Input image
    :param scale:
    :return:
    """

    # Obtain parameters for scaling
    height, width = img.shape[0], img.shape[1]
    img_scale = scale * width
    new_x, new_y = img.shape[1] * img_scale, img.shape[0] * img_scale

    # Rescale the image
    return cv2.resize(img, (int(new_x), int(new_y))), img_scale


def rescale_coordinates(coordinates, scale):
    """
    Resize the coordinates with the given scale
    :param coordinates: List of coordinates [x, y, w, h]
    :param scale: Number that resizes the coordinates
    :return: List containing the resized coodinates
    """
    return [int(item/scale) for item in coordinates]


def binarize_image(img):
    """Convert input image to binary image (Won't be used when integrated)"""

    # Convert image to grayscale image*
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # convert the grayscale image to binary image*
    #   - src: image source
    #   - threshold_value: The thresh value with respect to which the thresholding operation is made
    #   - max_BINARY_value: The value used with the Binary thresholding operations (to set the chosen pixels)
    _, thresh = cv2.threshold(gray_image, 127, 255, 0)

    return thresh


def get_centroid(img):
    """
    Given an image return the center of the image.
    :param img: Input image
    :return: x and y coordinates of the center of the image (cX and cY)
    """

    # calculate moments of binary image
    m = cv2.moments(img)

    # calculate x,y coordinate of center
    c_x = int(m["m10"] / m["m00"])
    c_y = int(m["m01"] / m["m00"])

    return c_x, c_y


def generate_wedge_mask(img, c_x, c_y, angle):
    """
    Given an an input image, its center coordinates and an angle, calculate it's correspondent wedge and generate
    an image mask.
    :param img: Input image.
    :param c_x: Center X coordinate of the input image.
    :param c_y: Center Y coordinate of the input image.
    :param angle: Angle of the desired wedge.
    :return: Image containing the generated mask of the wedge.
    """

    # Creating a right triangle with the given angle and coordinates
    # op_side = math.tan(math.radians(angle)) * c_x
    op_side = math.tan(math.radians(angle)) * img.shape[1]
    # c = [c_x, c_x * 2, c_x * 2]
    c = [0, img.shape[1], img.shape[1]]
    r = [c_y, c_y, int(c_y - op_side)]

    # Generate map of three points that compose the right triangle
    rc = np.array((c, r)).T

    # Create a mask
    mask = np.zeros_like(img)

    # Draw wedge on the mask
    cv2.drawContours(mask, [rc], 0, 255, -1)

    # return mask
    return mask


def extract_wedge(img, angle):
    """
    Extract a wedge of a given angle from the input image
    :param img: Input image
    :param bin_img: Binarized input image
    :param angle: Angle of the wedge
    :return: Image of wedge and image of wedge's mask
    """

    # Get the center coordinate (cX, cY) of the image
    # cX, cY = get_centroid(s_img)
    c_x, c_y = 0, img.shape[0]

    # Generate the mask for the wedge
    mask = generate_wedge_mask(img, c_x, c_y, angle)

    # Create two canvas
    wedge = np.zeros_like(img)

    # Create a blank canvas and extract Wedge from main image
    wedge[mask == 255] = img[mask == 255]

    # At this point we have extracted the wedge from the main image.
    # Now we proceed to isolate the area that contains only the wedge

    n_iterations = int((30 / 3600) * img.shape[1])
    # Create a mask of the extracted wedge
    _, mask = cv2.threshold(cv2.erode(cv2.dilate(wedge, None, iterations=n_iterations),
                                      None, iterations=n_iterations+2), 150, 255, cv2.THRESH_BINARY)

    # Find contours for the wedge
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Find the contour with the best area that covers the wedge.
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt = contours[max_index]

    # Get the coordinates of the bounding rectangle of the wedge.
    x, y, w, h = cv2.boundingRect(cnt)

    wedge = wedge[y:y + h, x:x + w]
    mask = mask[y:y + h, x:x + w]

    return wedge, mask


def find_max_ins_rect(data):
    """
    Find the largest inscribed rectangle of a given image map
    :param img: Input image
    :return: Largest Inscribed Rectangle Coordinates
    """

    # Resize the image mask(This is to speed up the calculations of largest inscribed rectangle)
    data, r_scale = resize_image(data, 125)

    # Extract a channel from the input image(RGB will be the same since image is binarized)
    nrows, ncols = data.shape[0], data.shape[1]
    w = np.zeros(dtype=int, shape=data.shape)
    h = np.zeros(dtype=int, shape=data.shape)
    skip = 0
    area_max = (0, [])

    # Iterate through each pixel and mark on w and h
    for r in range(nrows):
        for c in range(ncols):
            if data[r][c] == skip:
                continue
            if r == 255:
                h[r][c] = 1
            else:
                h[r][c] = h[r - 1][c] + 1
            if c == 255:
                w[r][c] = 1
            else:
                w[r][c] = w[r][c - 1] + 1
            minw = w[r][c]
            # Calculate the largest area and compare with the largest area stored
            for dh in range(h[r][c]):
                minw = min(minw, w[r - dh][c])
                area = (dh + 1) * minw
                if area > area_max[0]:
                    area_max = (area, [c - minw + 1, r - dh, c, r])

    # Coordinates of largest inscribed rectangle. List has the following order [x, y, w, h]
    rect_coor = area_max[1]

    # With the calculated scale, rescale the coordinates to obtain coordinates of the original image.
    return rescale_coordinates(rect_coor, r_scale)


def rotate_cuadrant(image, angle):
    """Given an image, make a rotation including its boundaries"""

    h, w = image.shape[0], image.shape[1]
    extra = np.zeros_like(image)
    extra = extra[:, int(w * .95):]
    image = np.append(image, extra, axis=1)

    # If input angle is 0, there is no need of rotating the image
    if angle != 0:
        M = cv2.getRotationMatrix2D((0, h), -1 * angle, 1)
        dst = cv2.warpAffine(image, M, (0, h))
        return dst
    else:
        return image


def extract_rectangle(img, img_mask):
    """
    Given a bounded wedge, extract its largest inscribed rectangle.
    :param img: image of bounded wedge
    :param img_mask: image mask of a bounded wedge.
    :return: Image containing the largest inscribed rectangle of the wedge
    """

    # Get coordinates of the largest inscribed rectangle a given wedge.
    coord = find_max_ins_rect(img_mask)
    x, y, w, h = coord[0], coord[1], coord[2], coord[3]

    # For Visual Testing
    # img2 = img.copy()
    # cv2.rectangle(img2, (x, y), (w, h), (0, 255, 0), 2)
    # show_image(img2)

    # With coordinates of rectangle obtain the rectangle from the wedge.
    img = img[y:h, x:w]
    # Rotate image 90 degrees
    return np.rot90(img).copy()


def extract_regions(img, n_rings, wedge_num):
    """
    Given a image containing a wedge rectangle, divide that image into regions
    :param img: Image containing extracted rectangle of wedge.
    :param n_rings: Number of rings
    :param wedge_num: Number of wedge that we're currently working with
    :return: Path where the region is stored
    """

    # Extract image shape properties
    height, width = img.shape[0], img.shape[1]
    # Calculate region height based on number rings
    region_height = int(height/n_rings)
    # Define starting points
    x, y = 0, height
    # Variable that will store regions path
    regions_path = str()
    # Defining type of image that will be used to store
    image_type = 'jpg'

    # For each region number, extract it's corresponding region.
    for region in range(n_rings):
        # Generate region name
        r_name = "R" + str(region + 1) + "W" + str(wedge_num)
        region_name = "R" + str(region + 1) + "W" + str(wedge_num) + "." + str(image_type)
        # Extract region from input image
        extracted_region = img[y - region_height:y, x:x + width]

        # Change coordinate for new region to extract
        y = y-region_height
        # Store region on dictionary
        append_regions_dict(r_name, extracted_region)
        # Store region on directory
        regions_path = store_region(extracted_region, region_name)

    return regions_path


def append_regions_dict(region_name, region):
    """
    Store a region image on a dictionary
    :param region_name: Name of the region "R(n)_W(m)"
    :param region: Image of the region (ndarray object)
    :return:None
    """
    global regions_list
    regions_list.update({region_name: region})


def store_region(img, img_name):
    """
    Store the given image on the file system
    :param img: Input image
    :param img_name: Name of the image
    :return: Path where the region is stored
    """

    regions_path = 'regions'
    intermediate_path = os.getcwd()
    full_path = os.path.join(intermediate_path, regions_path)

    # Check if regions_path exists, if not then create the path
    if not os.path.exists(full_path):
        try:
            os.mkdir(regions_path)
        except OSError:
            print("Creation of the directory %s failed" % regions_path)
        else:
            print("Successfully created the directory: %s " % regions_path)

    # Store region image
    try:
        cv2.imwrite(os.path.join(full_path, str(img_name)), img)
    except OSError:
        print("Storage of %s failed on path %s" % img_name % regions_path)
    else:
        print("Stored: ", os.path.join(full_path, str(img_name)))
        return full_path


def show_image(img):
    """
    Show on the screen a given image
    :param img: Input image
    :return: None
    """
    resized_img, _ = resize_image(img, 500)
    cv2.imshow('Image', resized_img)
    cv2.waitKey(0)


def region_extraction(bounded_input_image: np.ndarray, bounded_binarized_input_image: np.ndarray,
                      number_wedges: int, number_rings: int):
    """
    Extract regions from an input bamboo cross-section image.
    :param bounded_input_image: Input image bounded
    :param bounded_binarized_input_image: Input image binarized and bounded
    :param number_wedges: Integer with the number of wedges, specified by the user
    :param number_rings: Integer with the number of rings, specified by the user
    :return: None
    """

    # Validate Inputs
    assert type(number_wedges) is int, "Number of wedges has to be int."
    assert type(number_rings) is int, "Number of rings has to be int."
    assert 400 >= number_wedges >= 12, "Number of wedges should be between 12 and 400"
    assert (number_wedges % 4) == 0, "Number of wedges mus be divisible by 4"
    assert 25 >= number_rings >= 1, "Number of rings should be between 1 and 25"
    assert isinstance(bounded_input_image, np.ndarray), "bounded_input_image is wrong type"
    assert isinstance(bounded_binarized_input_image, np.ndarray), "bounded_binarized_input_image is wrong type"

    # Calculate the angle of the wedge given the number of wedges per quadrant
    wedge_angle = (lambda wedges: 360/wedges)(number_wedges)

    # Initialize variables
    current_angle = 0
    regions_path = str()
    wedge_number = 1

    # Iterate
    for cuadrant_num in range(4):

        image = np.rot90(bounded_binarized_input_image, 4-cuadrant_num).copy()

        # Extract Cuadrant
        height, width = image.shape[0], image.shape[1]
        image = image[:int(height/2), int(width/2):]

        for cuadrant_wedge_num in range(int(number_wedges/4)):

            # Rotate the image to the current calculated angle
            wedge = rotate_cuadrant(image, int(current_angle % 90))

            # Extract wedge and the wedge's mask from the rotated image
            wedge, wedge_mask = extract_wedge(wedge, wedge_angle)

            # Extract the largest inscribed rectangle from wedge.
            wedge = extract_rectangle(wedge, wedge_mask)

            # Extract regions from the extracted rectangle
            regions_path = extract_regions(wedge, number_rings, wedge_number)

            # Increment the current angle for the next iteration
            current_angle = current_angle + wedge_angle

            # Increment the wedge number
            wedge_number = wedge_number + 1

    # Print path where regions are stored
    print("Stored Regions at: " + regions_path)

    return regions_list


def region_extraction_module(num_wedges, num_of_rings):
    # Simulating User Inputs
    bin_image = cv2.imread('C:\\Users\\Caloj\\PycharmProjects\\Sprout_Unofficial\\control.jpg')
    bin_img = binarize_image(bin_image)
    dir_path = "C:/Users/Caloj/Desktop/Sprout_Images"
    os.chdir(dir_path)

    # Calling Region Extraction
    return region_extraction(bin_image, bin_img, num_wedges, num_of_rings)

# if __name__ == "__main__":
#     # Simulating User Inputs
#     num_wedges = 12
#     num_of_rings = 3
#     # bin_image = cv2.imread('bamboo_4800_LI.jpg')
#     bin_image = cv2.imread('control.png')
#     # bin_image = cv2.imread('angle_test.jpg')
#     bin_img = binarize_image(bin_image)
#     dir_path = "C:/Users/Caloj/Desktop/Sprout_Images"
#     os.chdir(dir_path)
#
#
#     # Calling Region Extraction
#     region_extraction(bin_img, num_wedges, num_of_rings)
#

