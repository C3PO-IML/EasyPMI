import unittest

import core.computations.baccino
from core.input_parameters import InputParameters
from core.output_results import BaccinoResults

data_test = [
    # --------------------- 
    (InputParameters(
        tympanic_temperature=30,
        ambient_temperature=15
    ), BaccinoResults(
        post_mortem_interval_interval=4.084666666666666,
        post_mortem_interval_global=4.325,
        confidence_interval_interval=1.6338666666666666,
        confidence_interval_global=1.7300000000000002
    )),
    # ---------------------
    (InputParameters(
        tympanic_temperature=30,
        ambient_temperature=20
    ), BaccinoResults(
        post_mortem_interval_interval=4.084666666666666,
        post_mortem_interval_global=4.883333333333334,
        confidence_interval_interval=1.6338666666666666,
        confidence_interval_global=1.9533333333333336
    )),
    # --------------------- Error Test
    (InputParameters(
        tympanic_temperature=300,
        ambient_temperature=15
    ), BaccinoResults(
        error_message="Any Error"
    )),
]


class Test(unittest.TestCase):
    def test_compute(self):
        # Test each case
        for input_parameters, expected_result in data_test:
            # Compute
            results = core.computations.baccino.compute(input_parameters)

            # Compare
            if expected_result.error_message:
                self.assertTrue(results.error_message, "Error expected\n" + str(input_parameters))
            else:
                self.assertEqual(expected_result.post_mortem_interval_interval, results.post_mortem_interval_interval,
                                 "Bad PostMortemInterval(Interval) with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.post_mortem_interval_global, results.post_mortem_interval_global,
                                 "Bad PostMortemInterval(Global) with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.confidence_interval_interval, results.confidence_interval_interval,
                                 "Bad ConfidenceInterval(Interval) with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.confidence_interval_global, results.confidence_interval_global,
                                 "Bad ConfidenceInterval(Global) with following inputs:\n" + str(input_parameters))
