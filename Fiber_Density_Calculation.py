import cv2
import copy
import Data_Management_Module
import Utils


def fiber_density_calculation(number_rings, number_wedges, raw_dictionary):
    """
    Calculates the fiber density of every png region image, found in the directory 'regions'
    :param number_rings: the number of rings, specified by the user, for the sample cross-section analysis.
    :param number_wedges: the number of wedges, specified by the user, for the sample cross-section analysis.
    :param raw_dictionary: dictionary containing raw image data
    :return: two dimensional list with the fiber density of every region. Rows correspond to the number of rings
             and columns correspond to the number of wedges.
    """

    # Validates that the number of rings and wedges received are within the established ranges.
    Utils.validate_parameters(number_rings, 0)
    Utils.validate_parameters(number_wedges, 1)

    # Initialize internal variables
    wedge_counter = 0
    ring_counter = 0
    column_wedges = []
    row_rings = []
    regions = number_rings * number_wedges
    image_path = 'regions'
    # Validates that the directory regions exists,
    Utils.validate_path(image_path)

    # Retrieve the path for every png file found in the directory 'regions'
    files = Utils.get_files_path(image_path, '.jpg')
    # Validates that the number of files matches the expected number of regions
    Utils.validate_number_regions(len(files), regions)
    # create a dictionary where the key is the regions (i.e R1W1) name and the value is its path.
    dictionary = Utils.sort_files(files)

    # Main loop that iterates through every region
    for i in range(regions):

        key = 'R' + str(ring_counter + 1) + 'W' + str(wedge_counter + 1)
        # Get region image path from dictionary
        try:
            # file_path = dictionary.get(key)
            image = raw_dictionary.get(key)
        except:
            raise Exception("Unable to open region image")

        # try:
        #     # read the image into the system
        #     image = cv2.imread(file_path, 0)
        # except:
        #     raise Exception("Unable to open region image")

        try:
            # Invert the image's black and white pixels
            inverted = cv2.bitwise_not(image)
        except:
            raise Exception("Unable to invert image")

        try:
            # Identify the white regions (fibers) of the image with the use of the connected component algorithm.
            # output holds and array with the area of each white region
            output = cv2.connectedComponentsWithStats(inverted)
        except:
            raise Exception("Unable to identify fibers")

        total_area = 0

        # Calculate the area of the whole region.
        for area in output[2]:
            total_area += area[4]
        # Calculate the area of fiber (total area - black pixels area)
        fiber_area = total_area - output[2][0][4]

        fiber_density = fiber_area / total_area

        column_wedges.append(fiber_density)

        wedge_counter += 1
        # Change to the next ring after all the densities  have been added
        if wedge_counter >= number_wedges:
            wedge_counter = 0
            ring_counter += 1
            row_rings.append(column_wedges)
            column_wedges = []
    return row_rings


def fiber_density_averages(fiber_density):
    """
    Calculates the average of every ring and every wedge of the provided list
    :param fiber_density: two dimensional list with the fiber density of every region.
    :return: two dimensional list with the fiber density of every region,
             with the averages of every wedge and every ring
    """
    fiber_density_with_average = copy.deepcopy(fiber_density)
    number_rings = len(fiber_density)
    number_wedges = len(fiber_density[0])
    # Sums the values of every column
    wedge_sum = [sum(x) for x in zip(*fiber_density)]

    wedge_averages = []
    # Calculates the average of each wedge
    for wedge in wedge_sum:
        average = wedge / number_rings
        wedge_averages.append(average)

    fiber_density_with_average.append(wedge_averages)
    # Calculates the average of each row
    for ring in fiber_density_with_average:
        ring_sum = sum(ring)
        ring_average = ring_sum / number_wedges
        ring.append(ring_average)

    return fiber_density_with_average


def fiber_density_and_distribution(number_rings, number_wedges, dictionary):
    """
    Main Fiber Density Module function to be called by the UI controller. This function will generate the fiber density
    list, with the averages, and send them to the Data Management Module.
    :param number_rings: the number of rings, specified by the user, for the sample cross-section analysis.
    :param number_wedges: the number of wedges, specified by the user, for the sample cross-section analysis.
    :param dictionary: dictionary containing raw image data TODO: isra revisa
    :return: None
    """
    fiber_density_list = fiber_density_calculation(number_rings, number_wedges, dictionary)
    Data_Management_Module.set_fiber_density(fiber_density_list)
    fiber_density_with_average = fiber_density_averages(fiber_density_list)
    Data_Management_Module.set_fiber_density_average(fiber_density_with_average)
