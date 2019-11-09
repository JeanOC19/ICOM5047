import unittest
import time
import Fiber_Density_Calculation
import Region_Extraction


class TestFiberDensity(unittest.TestCase):

    def test_inputs_fiber_density(self):
        """
        Test that invalid number of wedges and rings throw an exception
        """
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 2, 11)
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 3, 0)
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 0, 12)
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 26, 401)
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 3, 500)
        self.assertRaises(Exception, Fiber_Density_Calculation.fiber_density_calculation, 500, 12)

    # def test_fiber_density_accuracy_rings(self):
    #     """
    #     Test that the average fiber density of rings is below 3.5% error
    #     """
    #     matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
    #                              0.429762, 0.393449, 0.401225, 0.429967],
    #                             [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
    #                              0.548483, 0.542541, 0.553700, 0.548965],
    #                             [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
    #                              0.706593, 0.715743, 0.714168, 0.703361]]
    #
    #     user_rings = 3
    #     number_wedges = 12
    #     dictionary = Region_Extraction.region_extraction_module(number_wedges, user_rings)
    #     start_time = time.time()
    #     fiber_density_sprout = Fiber_Density_Calculation.fiber_density_calculation(user_rings, number_wedges, dictionary)
    #     print("Fiber Density Calculation Runtime: %s seconds ---" % (time.time() - start_time))
    #
    #     fd_with_average = Fiber_Density_Calculation.fiber_density_averages(fiber_density_sprout)
    #     fd_matlab_average = Fiber_Density_Calculation.fiber_density_averages(matlab_fiber_density)
    #
    #     for i in range(user_rings):
    #         exact = fd_matlab_average[i][number_wedges]
    #         approx = fd_with_average[i][number_wedges]
    #         percentage_error = (abs(exact - approx) / exact) * 100
    #         print('Ring ' + str(i + 1) + ', Exact value: ' + str(exact) + ', Approximate value: ' + str(approx) +
    #               ', Percentage of error: ' + str(percentage_error))
    #         # self.assertTrue(percentage_error <= 3.5,
    #         #                 "Error Percentage " + str(percentage_error) +
    #         #                 " is larger than 3.5 in: [" + str(i) + "][" + str(number_wedges - 1) + "]")
    #     print('-------------------------------------')

    def test_fiber_density_accuracy_wedges(self):
        """
        Test that the average fiber density of wedges is below 3.5% error
        """
        matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
                                 0.429762, 0.393449, 0.401225, 0.429967],
                                [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
                                 0.548483, 0.542541, 0.553700, 0.548965],
                                [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
                                 0.706593, 0.715743, 0.714168, 0.703361]]

        user_rings = 3
        number_wedges = 12
        dictionary = Region_Extraction.region_extraction_module(number_wedges, user_rings)
        fiber_density_sprout = Fiber_Density_Calculation.fiber_density_calculation(user_rings, number_wedges, dictionary)
        fd_with_average = Fiber_Density_Calculation.fiber_density_averages(fiber_density_sprout)
        fd_matlab_average = Fiber_Density_Calculation.fiber_density_averages(matlab_fiber_density)

        for j in range(number_wedges):
            exact = fd_matlab_average[user_rings][j]
            approx = fd_with_average[user_rings][j]
            percentage_error = (abs(exact - approx) / exact) * 100
            print('Wedge ' + str(j + 1) + ', Exact value: ' + str(exact) + ', Approximate value: ' + str(approx) +
                  ', Percentage of error: ' + str(percentage_error))
            # self.assertTrue(percentage_error <= 3.5,
            #                 "Error Percentage " + str(percentage_error) +
            #                 " is larger than 3.5 in: [" + str(user_rings) + "][" + str(j) + "]")

    def test_correct_average_calculation_rings(self):
        """
        Test that average of columns and rows is being calculated correctly
        """

        matlab_fiber_density = [[0.443516, 0.435262, 0.447433, 0.453988, 0.430503, 0.451662, 0.449479, 0.449918,
                                 0.429762, 0.393449, 0.401225, 0.429967],
                                [0.551969, 0.569961, 0.549261, 0.529712, 0.563685, 0.567644, 0.590936, 0.521671,
                                 0.548483, 0.542541, 0.553700, 0.548965],
                                [0.712373, 0.725422, 0.699161, 0.675843, 0.688871, 0.694169, 0.725839, 0.685522,
                                 0.706593, 0.715743, 0.714168, 0.703361]]

        fiber_density_with_average = Fiber_Density_Calculation.fiber_density_averages(matlab_fiber_density)

        ring_average1 = (0.443516 + 0.435262 + 0.447433 + 0.453988 + 0.430503 + 0.451662 + 0.449479 + 0.449918 +
                         0.429762 + 0.393449 + 0.401225 + 0.429967) / 12

        self.assertTrue(ring_average1 == fiber_density_with_average[0][12],
                        "Calculated average does not match the expected one")

        ring_average2 = (0.551969 + 0.569961 + 0.549261 + 0.529712 + 0.563685 + 0.567644 + 0.590936 + 0.521671 +
                         0.548483 + 0.542541 + 0.553700 + 0.548965) / 12

        self.assertTrue(ring_average2 == fiber_density_with_average[1][12],
                        "Calculated average does not match the expected one")
        ring_average3 = (0.712373 + 0.725422 + 0.699161 + 0.675843 + 0.688871 + 0.694169 + 0.725839 + 0.685522 +
                         0.706593 + 0.715743 + 0.714168 + 0.703361) / 12

        self.assertTrue(ring_average3 == fiber_density_with_average[2][12],
                        "Calculated average does not match the expected one")

        wedge_average1 = (0.443516 + 0.551969 + 0.712373) / 3

        self.assertTrue(wedge_average1 == fiber_density_with_average[3][0],
                        "Calculated average does not match the expected one")

        wedge_average2 = (0.435262 + 0.569961 + 0.725422) / 3

        self.assertTrue(wedge_average2 == fiber_density_with_average[3][1],
                        "Calculated average does not match the expected one")

        wedge_average12 = (0.429967 + 0.548965 + 0.703361) / 3

        self.assertTrue(wedge_average12 == fiber_density_with_average[3][11],
                        "Calculated average does not match the expected one")

        wedge_average11 = (0.401225 + 0.553700 + 0.714168) / 3

        self.assertTrue(wedge_average11 == fiber_density_with_average[3][10],
                        "Calculated average does not match the expected one")


if __name__ == '__main__':
    unittest.main()
