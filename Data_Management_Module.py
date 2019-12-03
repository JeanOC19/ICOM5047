import Global_Module
import csv
import matplotlib.pyplot as plt
import copy
import Utils


def set_fiber_density(fiber_density):
    """
    Setter for the fiber density list (without averages)
    :param fiber_density: two dimensional list that contains the fiber density of each region.
    :return: None
    """
    # Validate that the received list is not empty and has appropriate dimensions
    Utils.validate_fiber_list(fiber_density)
    Global_Module.global_fiber_density = fiber_density


def get_fiber_density():
    """
    Getter or the fiber density list (without averages)
    :return: two dimensional list that contains the fiber density of each region.
    """
    return Global_Module.global_fiber_density


def set_fiber_density_average(fiber_density_average):
    """
    Setter for the fiber density list with the averages of every ring and wedge.
    :param fiber_density_average: two dimensional list that contains the fiber density of each region. And the average
           of every ring and wedge
    :return: None
    """
    # Validate that the received list is not empty and has appropriate dimensions
    Utils.validate_fiber_list_average(fiber_density_average)
    Global_Module.global_fiber_density_with_average = fiber_density_average


def get_fiber_density_average():
    """
    Getter or the fiber density list, with averages
    :return: two dimensional list that contains the fiber density of each region. And the average
             of every ring and wedge
    """
    return Global_Module.global_fiber_density_with_average


def set_dimensional_measurements(dimensional_measurements):
    """
    Setter for the list of dimensional measurements
    :param dimensional_measurements: list of that contain the dimensional measurements of the sample cross-section,
    these are: Area, Outer Diameter, Inner Diameter, X coordinate of centroid, Y coordinate of centroid,
    X moment of inertia, Y moment of inertia, Product of Inertia
    :return: None
    """
    # Validate that the received list is not empty and has appropriate dimensions
    Utils.validate_dimension_list(dimensional_measurements)
    Global_Module.global_dimensional_measurements = dimensional_measurements


def get_dimensional_measurements():
    """
    Getter for the list of dimensional measurements
    :return: list of that contain the dimensional measurements of the sample cross-section,
    these are: Area, Outer Diameter, Inner Diameter, X coordinate of centroid, Y coordinate of centroid,
    X moment of inertia, Y moment of inertia, Product of Inertia
    """
    return Global_Module.global_dimensional_measurements


def set_diameters(diameters):
    """
    Setter for the list of inner and outer diameters of each wedge.
    :param diameters:  two dimensional list of that contain the inner and outer diameters of the sample cross-section.
    :return: None
    """
    # Validate that the received list is not empty and has appropriate dimensions
    Global_Module.global_diameters = diameters


def get_diameters():
    """
    Getter for the list of inner and outer diameters of each wedge
    :return: two dimensional list of that contain the inner and outer diameters of the sample cross-section.
    """
    return Global_Module.global_diameters


def save_fiber_density_csv(name, path):
    """
    Saves a csv file containing the fiber density of each region of the bamboo cross-section,
    with the averages of each ring and wedge
    :param name: file name that the user has specified for the csv.
    :param path: path that indicates the location of the directory where the csv file will be stored
    :return: None
    """
    # Validate that the file name given does not contain special characters
    Utils.validate_name(name)

    # Validate that the directory path exists
    Utils.validate_path(path)

    # Generate full path to store file
    file_path = Utils.get_path('_RegionFiberDensity.csv', name, path)

    # Get fiber density list with averages and validate that its dimensions are correct.
    fiber_density_og = get_fiber_density_average()
    Utils.validate_fiber_list_average(fiber_density_og)

    # Initialize variables
    fiber_density = copy.deepcopy(fiber_density_og)
    column_titles = []
    counter_wedges = 1
    column_titles.append('')
    counter_rings = 1
    number_columns = len(fiber_density[0])
    number_rows = len(fiber_density)

    # Fill column titles
    for i in range(number_columns - 1):
        column = 'W' + str(counter_wedges)
        column_titles.append(column)
        counter_wedges += 1
    column_titles.append('Averages')

    # Fill row titles
    for j in range(number_rows - 1):
        row = 'R' + str(counter_rings)
        fiber_density[j].insert(0, row)
        counter_rings += 1
    fiber_density[number_rows - 1].insert(0, 'Averages')

    # Create csv and save to local file system
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(column_titles)
        writer.writerows(fiber_density)

    # Validate that created csv was successfully saved
    Utils.validate_path(file_path)


def save_dimensional_measurements_csv(name, path, units):
    """
    Saves csv file containing the the dimensional measurements of the sample cross-section,
    these are: Area, Outer Diameter, Inner Diameter, X coordinate of centroid, Y coordinate of centroid,
    X moment of inertia, Y moment of inertia, Product of Inertia
    :param name: file name that the user has specified for the csv.
    :param path: path that indicates the location of the directory where the csv file will be stored
    :param units: units in which the data will be reported in the csv
    :return: None
    """
    # Validate that the file name given does not contain special characters
    Utils.validate_name(name)

    # Validate that the directory path exists
    Utils.validate_path(path)

    # Validate that the units received are supported
    Utils.validate_units(units)

    # Generate full path to store file
    file_path = Utils.get_path('_MeasurementData.csv', name, path)

    # Get dimensional measurements list and validate that its dimensions are correct.
    dimensional_measurements_og = get_dimensional_measurements()
    Utils.validate_dimension_list(dimensional_measurements_og)

    # Initialize variables
    area = 'Area ' + '(' + units + '^2' + ')'
    outer_diameter = 'Outer Diameter ' + '(' + units + ')'
    inner_diameter = 'Inner Diameter ' + '(' + units + ')'
    x_centroid = 'X Centroid ' + '(' + units + ')'
    y_centroid = 'Y Centroid ' + '(' + units + ')'
    x_moment = 'X Moment of Inertia ' + '(' + units + '^4' + ')'
    y_moment = 'Y Moment of Inertia ' + '(' + units + '^4' + ')'
    product_inertia = 'Product of Inertia ' + '(' + units + '^4' + ')'
    column_titles = [area, outer_diameter, inner_diameter, x_centroid, y_centroid, x_moment, y_moment, product_inertia]
    dimension_new = []
    for index in range(len(dimensional_measurements_og)):
        temporary = [column_titles[index], dimensional_measurements_og[index]]
        dimension_new.append(temporary)

    # Create csv and save to local file system
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(dimension_new)

    # Validate that created csv was successfully saved
    Utils.validate_path(file_path)
    save_diameter_csv(path, units, name)


def save_diameter_csv(path, units, file_name):
    """
    Save csv that contains the inner and outer diameters of the cross-section
    :param path: path that indicates the location of the directory where the csv file will be stored
    :param units: units in which the data will be reported in the csv
    :return: None
    """

    # Validate that the directory path exists
    Utils.validate_path(path)

    # Validate that the units received are supported
    Utils.validate_units(units)

    # Generate full path to store file
    file_path = Utils.get_path('_BambooDiameters.csv', file_name, path)

    # Get diameters list and validate that its dimensions are correct.
    diameters_og = get_diameters()
    Utils.validate_diameter_list(diameters_og)

    # Initialize variables
    diameters = []
    for index in range(len(diameters_og[0])):
        temp = [diameters_og[0][index], diameters_og[1][index]]
        diameters.append(temp)
    outer_diameter = 'Outer Diameter ' + '(' + units + ')'
    inner_diameter = 'Inner Diameter ' + '(' + units + ')'
    column_titles = ['Measurement', outer_diameter, inner_diameter]
    counter_diameter = 1
    number_rows = len(diameters)

    # Set row titles
    for j in range(number_rows):
        row = str(counter_diameter)
        diameters[j].insert(0, row)
        counter_diameter += 1

    # Create csv and save to local file system
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(column_titles)
        writer.writerows(diameters)

    # Validate that created csv was successfully saved
    Utils.validate_path(file_path)


def save_graph_fiber_vs_wedges(name, path):
    """
    Saves a Fiber vs. Wedges linear graph to the local file system as a jpg file
    :param name: file name that the user has specified for the graph image
    :param path: path that indicates the location of the directory where the graph image will be stored
    :return: None
    """
    # Validate that the file name given does not contain special characters
    Utils.validate_name(name)

    # Validate that the directory path exists
    Utils.validate_path(path)

    # Generate full path to store image
    graph_path = Utils.get_path('_RingGraph.jpg', name, path)

    # Get fiber density list (without averages) and validate its dimensions
    fiber_density = get_fiber_density()
    Utils.validate_fiber_list(fiber_density)

    # Initialize variables
    number_columns = len(fiber_density[0])
    x = range(1, number_columns + 1)

    # Clear any previous graph still in memory
    plt.clf()

    # Change font size to 14pt
    plt.rcParams.update({'font.size': 14})

    # Graph lines, each line represents the fiber densities of the wedges across a ring.
    # Points in the graph: (Number of wedge, Fiber Density)
    for row in fiber_density:
        y = row

        # Graph title
        plt.title('Fiber Density vs. Wedges')

        # Y axis title
        plt.ylabel('Fiber Density')

        # X axis title
        plt.xlabel("Wedges")

        # Plot line
        plt.plot(x, y)

    fig = plt.gcf()

    # Increase image size
    fig.set_size_inches(18.5, 10.5)

    # Store image in local file system
    fig.savefig(graph_path, dpi=100)

    # Validate that the image was successfully saved
    Utils.validate_path(graph_path)


def save_graph_fiber_vs_rings(name, path):
    """
    Saves a Fiber vs. Rings linear graph to the local file system as a jpg file
    :param name: file name that the user has specified for the graph image
    :param path: path that indicates the location of the directory where the graph image will be stored
    :return: None
    """
    # Validate that the file name given does not contain special characters
    Utils.validate_name(name)

    # Validate that the directory path exists
    Utils.validate_path(path)

    # Generate full path to store image
    graph_path = Utils.get_path('_WedgeGraph.jpg', name, path)

    # Get fiber density list (without averages) and validate its dimensions
    fiber_density = get_fiber_density()
    Utils.validate_fiber_list(fiber_density)

    # Initialize variables
    number_rows = len(fiber_density)
    x = range(1, number_rows + 1)
    wedges = []
    [wedges.append(x) for x in zip(*fiber_density)]

    # Clear any previous graph still in memory
    plt.clf()

    # Change font size to 14pt
    plt.rcParams.update({'font.size': 14})

    # Graph title
    plt.title('Fiber Density vs. Rings')

    # Y axis title
    plt.ylabel('Fiber Density')

    # X axis title
    plt.xlabel("Rings")

    if len(x) == 1:
        for columns in wedges:
            for value in columns:
                # Plot points
                plt.plot(1, value, 'o')
    else:
        # Graph lines, each line represents the fiber densities of the rings across a wedge.
        # Points in the graph: (Number of ring, Fiber Density)
        for columns in wedges:
            y = columns

            # Plot line
            plt.plot(x, y)

    # Show every value in the x axis
    plt.xticks(x)
    fig = plt.gcf()

    # Increase image size
    fig.set_size_inches(18.5, 10.5)

    # Store image in local file system
    fig.savefig(graph_path, dpi=100)

    # Validate that the image was successfully saved
    Utils.validate_path(graph_path)


def save_graphs(name, path):
    """
    Main function that calls both save graph functions. To be called by the UI controller to store the two graph images
    :param name: file name that the user has specified for the graph image
    :param path: path that indicates the location of the directory where the graph image will be stored
    :return: None
    """
    # Generate Fiber Density vs. Wedges graph
    save_graph_fiber_vs_wedges(name, path)

    # Generate Fiber Density vs. Rings graph
    save_graph_fiber_vs_rings(name, path)
