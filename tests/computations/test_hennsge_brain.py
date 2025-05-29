# tests/computations/test_hennsge_brain.py

import unittest

import core.computations.henssge_brain
from core.input_parameters import InputParameters
from core.output_results import HenssgeBrainResults

data_test = [
    # --------------------- 
    (InputParameters(
        tympanic_temperature=30,
        ambient_temperature=15
    ), HenssgeBrainResults(
        post_mortem_interval=4.06373732394629,
        confidence_interval=1.5
    )),
    # ---------------------
    (InputParameters(
        tympanic_temperature=30,
        ambient_temperature=20
    ), HenssgeBrainResults(
        post_mortem_interval=5.2608129668058226,
        confidence_interval=1.5
    )),
    # --------------------- Error Test
    (InputParameters(
        tympanic_temperature=300,
        ambient_temperature=15
    ), HenssgeBrainResults(
        error_message="Any Error"
    )),
]


class Test(unittest.TestCase):
    def test_compute(self):
        # Test each case
        for input_parameters, expected_result in data_test:
            # Compute
            results = core.computations.henssge_brain.compute(input_parameters)

            # Compare
            if expected_result.error_message:
                self.assertTrue(results.error_message, "Error expected\n" + str(input_parameters))
            else:
                self.assertEqual(expected_result.post_mortem_interval, results.post_mortem_interval,
                                 "Bad PostMortemInterval with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.confidence_interval, results.confidence_interval,
                                 "Bad ConfidenceInterval with following inputs:\n" + str(input_parameters))
