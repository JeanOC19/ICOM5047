import cv2
import numpy as np
import math
import os

n_regions = 0 # for test purposes

# Added This
regions_list = dict()


def resize_image(img, scale):
    """
    Resize an image
    :param img: Input image
    :param scale:
    :return:
    """

    # # Load image
    # img = cv2.imread(img_path)

    # Obtain parameters for scaling
    height, width, depth = img.shape
    imgScale = scale / width
    newX, newY = img.shape[1] * imgScale, img.shape[0] * imgScale

    # Rescale the image
    return cv2.resize(img, (int(newX), int(newY))), imgScale


def rescale_coordinates(coordinates, scale):
    """
    Resize the coodinates with the given scale
    :param coordinates: List of coordinates [x, y, w, h]
    :param scale: Number that resizes the coordinates
    :return: List containing the resized coodinates
    """
    return [int(item/scale) for item in coordinates]


def create_mask(img):
    """
    Create mask out of input image
    :param img: Input image object
    :return: Array with zero values with same shape as the input image
    """
    return np.zeros_like(img)


def binarize_image(img):
    """Convert input image to binary image (Won't be used when integrated)"""

    # Convert image to grayscale image*
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # convert the grayscale image to binary image*
    #   - src: image source
    #   - threshold_value: The thresh value with respect to which the thresholding operation is made
    #   - max_BINARY_value: The value used with the Binary thresholding operations (to set the chosen pixels)
    ret, thresh = cv2.threshold(gray_image, 127, 255, 0)

    return thresh

def get_centroid(img):
    """
    Given an image return the center of the image.
    :param img: Input image
    :return: x and y coordinates of the center of the image (cX and cY)
    """

    # calculate moments of binary image
    M = cv2.moments(img)

    # calculate x,y coordinate of center
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    return cX, cY


def generate_wedge_mask(img, cX, cY, angle):
    """
    Given an an input image, its center coodinates and an angle, calculate it's correspondent wedge and generate
    an image mask.
    :param img: Input image.
    :param cX: Center X coordinate of the input image.
    :param cY: Center Y coordinate of the input image.
    :param angle: Angle of the desired wedge.
    :return: Image containing the generated mask of the wedge.
    """

    # Creating a right triangle with the given angle and coordinates
    op_side = math.tan(math.radians(angle)) * cX
    c = [cX, cX * 2, cX * 2]
    r = [cY, cY, int(cY - op_side)]

    # Generate map of three points that compose the right triangle
    rc = np.array((c, r)).T

    # Create a mask
    mask = create_mask(img)

    # Draw wedge on the mask
    cv2.drawContours(mask, [rc], 0, 255, -1)

    return mask


def extract_wedge(img, bin_img, angle):
    """
    Extract a wedge of a given angle from the input image
    :param img: Input image
    :param bin_img: Binarized input image
    :param angle: Angle of the wedge
    :return: Image of wedge and image of wedge's mask
    """

    # Get the center coordinate (cX, cY) of the image
    cX, cY = get_centroid(bin_img)

    # Generate the mask for the wedge
    wedge_mask = generate_wedge_mask(bin_img, cX, cY, angle)

    # Create a blank canvas and extract Wedge from main image
    wedge = np.zeros_like(img)
    wedge[wedge_mask == 255] = img[wedge_mask == 255]

    # At this point we have extracted the wedge from the main image.
    # Now we proceed to isolate the area that contains only the wedge

    # Create a mask of the extracted wedge
    img_dilation = cv2.dilate(wedge, None, iterations=14)
    img_erosion = cv2.erode(img_dilation, None, iterations=14)
    ret, thresh = cv2.threshold(img_erosion, 125, 255, cv2.THRESH_BINARY)

    # Find contours for the wedge
    edged = cv2.Canny(thresh, 250, 500)
    contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Find the contour with the best area that covers the wedge.
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt = contours[max_index]

    # Get the coordinates of the bounding rectangle of the wedge.
    x, y, w, h = cv2.boundingRect(cnt)

    # # For testing
    # cv2.drawContours(wedge,contours,-1,(0,255,0),3)
    # show_image(resize_image(wedge))
    # wedge2=wedge.copy()
    # rect = cv2.rectangle(wedge2, (x, y), (x+w,y+h), (0,255,0), 2)
    # show_image(resize_image(wedge2))

    return wedge[y:y + h, x:x + w], thresh[y:y + h, x:x + w]


def find_max_ins_rect(img):
    """
    Find the largest inscribed rectangle of a given image map
    :param img: Input image
    :return: Largest Inscribed Rectangle Coordinates
    """

    # Resize the image mask(This is to speed up the calculations of largest inscribed rectangle)
    rmask, rmask_scale = resize_image(img, 175)

    # Extract a channel from the input image(RGB will be the same since image is binarized)
    data = img[1:, 1:, 1]
    nrows, ncols = data.shape
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
    return rescale_coordinates(rect_coor, rmask_scale)


def rotate_bound(image, angle):
    """Given an image, make a rotation including its boundaries"""

    # If input angle is 0, there is no need of rotating the image
    if angle != 0:
        # grab the dimensions of the image and then determine the center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (nW, nH))
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
    # With coordinates of rectangle obtain the rectangle from the wedge.
    rect = img[coord[1]:coord[3], coord[0]:coord[2]]
    # Rotate image 90 degrees
    res = rotate_bound(rect, 90)

    return res


def extract_regions(img, n_rings, wedge_num):
    """
    Given a image containing a wedge rectangle, divide that image into regions
    :param img: Image containing extracted rectangle of wedge.
    :param n_rings: Number of rings
    :param wedge_num: Number of wedge that we're currently working with
    :return: Path where the region is stored
    """

    # Extract image shape properties
    height, width, depth = img.shape
    # Calculate region height based on number rings
    region_height = int(height/n_rings)
    # Define starting points
    x, y = 0, height
    # Variable that will store regions path
    regions_path = str()
    # Defining type of image that will be used to store
    image_type = 'png'

    # For each region number, extract it's corresponding region.
    for region in range(n_rings):
        # Generate region name
        region_name = "R" + str(region + 1) + "W" + str(wedge_num) + "." + str(image_type)
        # Extract region from input image
        extracted_region = img[y - region_height:y, x:x + width]
        # Change coordinate for new region to extract
        y = y-region_height
        # Store region on directory
        regions_path = store_region(extracted_region, region_name)
        # Increment global n_regions variable
        increment_n_regions()
        # TODO: Delete this
        append_regions_dict(region_name, extracted_region)

    return regions_path


def store_region(img, img_name):
    """
    Store the given image on the file system
    :param img: Input image
    :param img_name: Name of the image
    :return: Path where the region is stored
    """

    regions_path = '\\regions'
    full_path = os.path.join(os.getcwd(), regions_path)

    # Check if regions_path exists, if not then create the path
    if not os.path.exists(full_path):
        try:
            os.mkdir(os.getcwd() + '\\regions')
        except OSError:
            print("Creation of the directory %s failed" % regions_path)
        else:
            print("Successfully created the directory %s " % regions_path)

    # Store region image
    try:
        cv2.imwrite(os.path.join(full_path, str(img_name)), img)
    except OSError:
        print("Storage of %s failed on path %s" % img_name % regions_path)
    else:
        print("Stored: ", os.path.join(full_path, str(img_name)))
        return full_path


def increment_n_regions():
    global n_regions
    n_regions = n_regions+1


# ADDED THIS
def append_regions_dict(regionname, region):
    global regions_list
    regions_list.update({regionname: region})


def show_image(img):
    """Show on the screen a given image (For debug purposes)"""
    cv2.imshow('Image', img)
    cv2.waitKey(0)


def region_extraction(bounded_input_image, bounded_binarized_input_image, number_wedges, number_rings):
    """
    Extract regions from an input bamboo cross-section image.
    :param bounded_input_image: Input image bounded
    :param bounded_binarized_input_image: Input image binarized and bounded
    :param number_wedges: Integer with the number of wedges, specified by the user
    :param number_rings: Integer with the number of rings, specified by the user
    :return: None
    """

    # For Testing
    num_of_regions = number_wedges * number_rings
    print("Number of Expected Regions: ", num_of_regions)

    # Calculate the angle of the wedge given the number of wedges per quadrant
    wedge_angle = (lambda wedges: 360/wedges)(number_wedges)

    # Initialize variables
    current_angle = 0
    regions_path = str()
    wedge_number = 1

    while current_angle < 360:
        # Rotate the image to the current calculated angle
        rotated_image = rotate_bound(bounded_binarized_input_image, current_angle)
        # Extract wedge and the wedge's mask from the rotated image
        wedge, wedge_mask = extract_wedge(rotated_image, bin_img, wedge_angle)
        # Extract the largest inscribed rectangle from wedge.
        wedge_rectangle = extract_rectangle(wedge, wedge_mask)
        # Extract regions from the extracted rectangle
        regions_path = extract_regions(wedge_rectangle, num_of_rings, wedge_number)
        # Increment the current angle for the next iteration
        current_angle = current_angle + wedge_angle
        # Increment the wedge number
        wedge_number = wedge_number + 1

    print("Total Number of Regions: ", n_regions)
    print("Stored Regions at: " + regions_path)

    return None


if __name__ == "__main__":
    num_wedges_p_q = 12
    num_of_rings = 3
    dir_path = "C:\\Users\\Caloj\\Desktop\\Sprout_Images"
    image_type = ".png"
    rgb_image = cv2.imread('control_rgb.jpg')
    bin_image = cv2.imread('control.png')
    bin_img = binarize_image(bin_image)

    Regions_Path = region_extraction(rgb_image, bin_image, num_wedges_p_q, num_of_rings)

    # Call Fiber Density Module


