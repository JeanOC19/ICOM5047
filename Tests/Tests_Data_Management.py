import unittest
import os
import Data_Management_Module
import Fiber_Density_Calculation


class TestDataManagement(unittest.TestCase):

    def test_names(self):
        """
        Test that a name for files being store cannot contain special characters and that it must be a string
        """
        Fiber_Density_Calculation.fiber_density_and_distribution(3, 12)
        special_characters = ['<', '>', ':', '/', '\\', '|', '?', '*', '"']
        path = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder'
        units = 'cm'
        for c in special_characters:
            name = "Test" + c
            self.assertRaises(Exception, Data_Management_Module.save_fiber_density_csv, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_dimensional_measurements_csv, name, path, units)
            self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_wedges, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_rings, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_graphs, name, path)

            name = 800

            self.assertRaises(Exception, Data_Management_Module.save_fiber_density_csv, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_dimensional_measurements_csv, name, path, units)
            self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_wedges, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_rings, name, path)
            self.assertRaises(Exception, Data_Management_Module.save_graphs, name, path)

    def test_units(self):
        """
        Test that if units provided are not supported system will throw an exception
        """
        Fiber_Density_Calculation.fiber_density_and_distribution(3, 12)
        dimensional_measurements = [1, 2, 3, 4, 5, 6, 7, 8]
        Data_Management_Module.set_dimensional_measurements(dimensional_measurements)
        diameters = []
        for i in range(12):
            diameters.append([1, 2])
        Data_Management_Module.set_diameters(diameters)
        path = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder'
        units = 'm'
        name = "Test"
        self.assertRaises(Exception, Data_Management_Module.save_dimensional_measurements_csv, name, path, units)
        self.assertRaises(Exception, Data_Management_Module.save_diameter_csv, path, units)

    def test_paths(self):
        """
        Test that if the path of the directory
        where the file will be saved does not exist the system will raise an exception
        """
        Fiber_Density_Calculation.fiber_density_and_distribution(3, 12)
        dimensional_measurements = [1, 2, 3, 4, 5, 6, 7, 8]
        Data_Management_Module.set_dimensional_measurements(dimensional_measurements)
        diameters = []
        for i in range(12):
            diameters.append([1, 2])
        Data_Management_Module.set_diameters(diameters)
        path = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folde'
        units = 'cm'
        name = "Test"
        self.assertRaises(Exception, Data_Management_Module.save_fiber_density_csv, name, path)
        self.assertRaises(Exception, Data_Management_Module.save_dimensional_measurements_csv, name, path, units)
        self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_wedges, name, path)
        self.assertRaises(Exception, Data_Management_Module.save_graph_fiber_vs_rings, name, path)
        self.assertRaises(Exception, Data_Management_Module.save_graphs, name, path)
        self.assertRaises(Exception, Data_Management_Module.save_diameter_csv, path, units)

    def test_csv_files_saved_correctly(self):
        """
        Test that csv files are being stored with correct name, correct file type and in the correct directory
        """
        Fiber_Density_Calculation.fiber_density_and_distribution(3, 12)
        dimensional_measurements = [1, 2, 3, 4, 5, 6, 7, 8]
        Data_Management_Module.set_dimensional_measurements(dimensional_measurements)
        diameters = []
        for i in range(12):
            diameters.append([1, 2])
        Data_Management_Module.set_diameters(diameters)
        path = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder'
        units = 'cm'

        Data_Management_Module.save_fiber_density_csv('FDTest', path)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\FDTest_RegionFiberDensity.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

        Data_Management_Module.save_fiber_density_csv('FDTest', path)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\FDTest1_RegionFiberDensity.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

        Data_Management_Module.save_dimensional_measurements_csv('DTest', path, 'cm')
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\DTest_AdditionalData.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

        Data_Management_Module.save_dimensional_measurements_csv('DTest', path, 'cm')
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\DTest1_AdditionalData.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

        Data_Management_Module.save_diameter_csv(path, units)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Bamboo_Diameters.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

        Data_Management_Module.save_diameter_csv(path, units)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Bamboo_Diameters1.csv'
        self.assertTrue(os.path.exists(expected_output), "File was not properly saved")

    def test_graph_files_saved_correctly(self):
        """
        Test that graph images are being stored with correct name, correct file type and in the correct directory
        """
        Fiber_Density_Calculation.fiber_density_and_distribution(3, 12)
        path = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder'

        Data_Management_Module.save_graphs('Graph', path)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Graph_RingGraph.jpg'
        expected_output1 = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Graph_WedgeGraph.jpg'
        self.assertTrue(os.path.exists(expected_output), "Graph was not properly saved")
        self.assertTrue(os.path.exists(expected_output1), "Graph was not properly saved")

        Data_Management_Module.save_graphs('Graph', path)
        expected_output = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Graph1_RingGraph.jpg'
        expected_output1 = 'C:\\Users\\israe\\Desktop\\Capstone\\Test_Folder\\Graph1_WedgeGraph.jpg'
        self.assertTrue(os.path.exists(expected_output), "Graph was not properly saved")
        self.assertTrue(os.path.exists(expected_output1), "Graph was not properly saved")

    def test_set_dimensional_measurements(self):
        """
        Test that the system will not store a dimensional measurement list with invalid dimensions
        """
        dimensional_measurements = []
        self.assertRaises(Exception, Data_Management_Module.set_dimensional_measurements, dimensional_measurements)
        dimensional_measurements = [1, 2, 3, 4, 5, 6, 7]
        self.assertRaises(Exception, Data_Management_Module.set_dimensional_measurements, dimensional_measurements)
        dimensional_measurements = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.assertRaises(Exception, Data_Management_Module.set_dimensional_measurements, dimensional_measurements)

    def test_set_diameters(self):
        """
        Test that the system will not store a diameters list with invalid dimensions
        """
        diameters = []
        self.assertRaises(Exception, Data_Management_Module.set_diameters, diameters)
        diameters = [[3.1, 4.5], [0.7, 6.8], [0.6, 6], [0.7, 8], [0.9, 10], [0.11, 12], [3.1, 4.5], [0.7, 6.8],
                     [0.6, 6], [0.7, 8], [0.9, 10]]
        self.assertRaises(Exception, Data_Management_Module.set_diameters, diameters)
        diameters1 = []
        for i in range(401):
            diameters.append([1, 2])
        self.assertRaises(Exception, Data_Management_Module.set_diameters, diameters1)
        diameters = [[3.1], [0.7], [0.6], [0.7], [0.9], [0.11], [3.1], [0.7], [0.6], [0.7], [0.9], [0.7]]
        self.assertRaises(Exception, Data_Management_Module.set_diameters, diameters)
        diameters = [[3.1, 4.5, 3], [0.7, 6.8, 3], [0.6, 6, 3], [0.7, 8, 3], [0.9, 10, 3], [0.11, 12, 3], [3.1, 4.5, 3],
                     [0.7, 6.8, 3], [0.6, 6, 3], [0.7, 8, 3], [0.9, 10, 3], [0.2, 4, 5]]
        self.assertRaises(Exception, Data_Management_Module.set_diameters, diameters)

    def test_set_fiber_density(self):
        """
        Test that the system will not store a fiber density list with invalid dimensions
        """
        fiber_density = []
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density, fiber_density)
        fiber_density = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density, fiber_density)
        fiber_density = [[1], [2], [3]]
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density, fiber_density)
        fiber_density1 = []
        for i in range(26):
            fiber_density1.append([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density, fiber_density1)
        fiber_density2 = [[], [], []]
        for row in fiber_density2:
            for i in range(401):
                row.append(i)
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density, fiber_density2)

    def test_set_fiber_density_average(self):
        """
        Test that the system will not store a fiber density with averages list with invalid dimensions
        """
        fd_average = []
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density_average, fd_average)
        fd_average = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]]
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density_average, fd_average)
        fd_average = [[1], [2], [3], [4]]
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density_average, fd_average)
        fd_average1 = []
        for i in range(27):
            fd_average1.append([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density_average, fd_average1)
        fd_average2 = [[], [], [], []]
        for row in fd_average2:
            for i in range(402):
                row.append(i)
        self.assertRaises(Exception, Data_Management_Module.set_fiber_density_average, fd_average2)


if __name__ == '__main__':
    unittest.main()
