import os


class InvalidInput(Exception):
    message = Exception


def validate_name(name):
    """
    Validates that the name provided by the user is a string and does not contain any special characters
    and can be used as a file name.
    :param name: file name that the user has specified for the graph image or csv
    :return: None
    """
    # Validates that provided name is a string, raises and exception otherwise.
    is_string = isinstance(name, str)
    if not is_string:
        raise InvalidInput('Exception: Name is not a string')
    special_characters = ['<', '>', ':', '/', '\\', '|', '?', '*', '"']

    # Validates that provided name does not contain any special characters.
    for c in special_characters:
        if c in name:
            raise InvalidInput('Exception: Name contains special characters')


def validate_path(path):
    """
    Validates that the provided path exists
    :param path: path of a directory or a file
    :return: None
    """
    # If path does not exist, it raises an error
    if not (os.path.exists(path)):
        raise InvalidInput('Exception: ' + path + 'does not exist')


def validate_units(units):
    """
    Validates that units provided by user are supported by the system
    :param units: units in which the data will be reported in the csv
    :return: None
    """
    # If units provided are not supported, it raises an error
    accepted_units = ['cm', 'in', 'mm']
    if units not in accepted_units:
        raise InvalidInput('Exception: Specified unit is not supported')


def validate_parameters(parameter, param_type):
    """
    Validates that number of rings or number of wedges are within the accepted range
    :param parameter: number of rings or number of wedges to be validated
    :param param_type: specifies wether parameter is a ring (0) or a wedge (1)
    :return: None
    """
    # Parameter is a ring
    if param_type == 0:
        # If ring number is less than three or larger than 25 raise an exception
        if parameter < 1 or parameter > 25:
            raise InvalidInput('Exception: Invalid number of rings')
    # Parameter is a wedge
    elif param_type == 1:
        # If wedge number is less than 12 or larger than 400 raise an exception.
        if parameter < 12 or parameter > 400:
            raise InvalidInput('Exception: Invalid number of wedges')


def validate_number_regions(number_files, number_regions):
    """
    Validate that the number of files in regions directory matches number of regions
    :param number_files: number of files in the regions directory
    :param number_regions: number of regions to be analysed
    :return: None
    """
    # If number of files does not match number of regions, raise an exception
    if number_files != number_regions:
        raise InvalidInput('Exception: Number of files does not match number of regions')


def validate_fiber_list(list):
    """
    Validate that the dimensions of the fiber density list are appropriate
    :param list: two dimensional list containing fiber densities
    :return: None
    """
    # If list is empty raise an exception
    if not list:
        raise InvalidInput('Exception: fiber density list is empty')
    rows = len(list)

    # If rows are less than 1 or larger than 25 raise an exception since it does not match rings max. and min.
    if rows < 1 or rows > 25:
        raise InvalidInput('Exception: fiber density list has less than three rings')
    columns = len(list[0])

    # If columns are less than 12 or larger than 400 raise an exception since it does not match wedges max. and min.
    if columns < 12 or columns > 400:
        raise InvalidInput('Exception: fiber density list has less than twelve wedges')


def validate_fiber_list_average(list):
    """
    Validate that the dimensions of the fiber density with averages list are appropriate
    :param list: two dimensional list containing fiber densities with averages
    :return: None
    """
    # If list is empty raise an exception
    if not list:
        raise InvalidInput('Exception: fiber density list is empty')
    rows = len(list)

    # If rows are less than 4 or larger than 26 raise an exception since it does not match rings max. and min.
    # min. is 1 ring rows + 1 average row and max. is 25 ring rows + 1 average row
    if rows < 2 or rows > 26:
        raise InvalidInput('Exception: fiber density list has less than three rings')
    columns = len(list[0])

    # If columns are less than 13 or larger than 401 raise an exception since it does not match wedges max. and min.
    # min. is 12 wedge columns + 1 average column and max. is 400 wedge columns + 1 average column
    if columns < 13 or columns > 401:
        raise InvalidInput('Exception: fiber density list has less than twelve wedges')


def validate_dimension_list(list):
    """
    Validate that the dimensions of the dimensional measurements list are appropriate
    :param list: list that contains the dimensional measurements of the sample cross-section,
                 these are: Area, Outer Diameter, Inner Diameter, X coordinate of centroid, Y coordinate of centroid,
                 X moment of inertia, Y moment of inertia, Product of Inertia
    :return: None
    """
    # If list is empty raise an exception
    if not list:
        raise InvalidInput('Exception: dimensional measurement list is empty')
    measurements = len(list)

    # If length of list is not 8 raise an exception, since the amount of measurements is incorrect
    if measurements != 9:
        raise InvalidInput('Exception: number of elements in the list is incorrect')


def validate_diameter_list(list):
    """
    Validate that the dimensions of the diameter list are appropriate
    :param list: list containing the inner and outer diameters of the cross-section
    :return: None
    """
    # If list is empty raise an exception
    if not list:
        raise InvalidInput('Exception: dimensional measurement list is empty')
    columns = len(list)

    # If number of columns is not 2 raise an exception since there should be a column for inner diameters
    # and a second one for outer diameters
    if columns != 3:
        raise InvalidInput('Exception: number of columns in the list is incorrect')
    rows = len(list[0])

    # If number of rows is not a multiple of 4 raise exception
    if not(rows % 4 == 0):
        raise InvalidInput('Exception: number of rows in the list is incorrect')


def get_files_path(directory_path, file_type):
    """
    Generate a list with all the files of a certain file type contained in a specified directory
    :param directory_path: path of the directory to be explored
    :param file_type: file types that will be considered when collecting the paths of the files inside the directory
    :return: list of the paths of every file inside of the directory
    """
    file_paths = []

    # root: root directory, f: file, directories: directories inside root
    # generates the file names in a directory tree by traversing the tree
    for root, directories, f in os.walk(directory_path):
        for pic in f:
            if file_type in pic:
                file_string = os.path.join(root, pic)
                file_paths.append(file_string)
    return file_paths


def sort_files(file_list):
    """
    Generate a dictionary where the region name is the key and path is the value
    :param file_list: list of region paths
    :return: dictionary where the region name is the key and path is the value
    """
    file_dictionary = {}
    for file in file_list:
        # Separate string into elements
        file_split = (file.split('\\'))

        # Take the file name and file type element
        file_name = file_split[len(file_split) - 1]

        # Remove file type
        file_type_split = (file_name.split('.'))
        file_key = file_type_split[0]

        # Store file name (region name) as key and the path as its value
        file_dictionary[file_key] = file
    return file_dictionary


def get_path(default, name, path):
    """
    Generate a full path for a file to be stored
    :param default: default name that will be appended to file name (i.e _GraphWedge)
    :param name: name that the user has provided for the file
    :param path: path of the directory where the file will be saved
    :return: full path where file will be saved
    """
    counter = 1
    # Append directory path with file name and default name
    file_path = path + '\\' + name + default

    # Verify if this path exists, if it does exist add a number after file name and verify again.
    # Continue this loop, increasing the appended number, until the file path does not exist.
    while os.path.exists(file_path):
        file_path = path + '\\' + name + str(counter) + default
        counter += 1
    return file_path