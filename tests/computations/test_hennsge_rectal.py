# tests/computations/test_hennsge_rectal.py

import unittest

import core.computations.henssge_rectal
from core.constants import BodyCondition, EnvironmentType, SupportingBase
from core.input_parameters import InputParameters
from core.output_results import HenssgeRectalResults

data_test = [
    # --------------------- 
    (InputParameters(
        rectal_temperature=30,
        ambient_temperature=15,
        body_mass=80,
        body_condition=BodyCondition.NAKED,
        environment=EnvironmentType.MOVING_AIR,
        supporting_base=SupportingBase.WET_LEAVES
    ), HenssgeRectalResults(
        post_mortem_interval=23.29805995140954,
        confidence_interval=2.8,
        thermal_quotient=0.6756756756756755,
        corrective_factor=1.983
    )),
    # ---------------------
    (InputParameters(
        rectal_temperature=30,
        ambient_temperature=20,
        body_mass=80,
        body_condition=BodyCondition.WARMLY,
        environment=EnvironmentType.STILL_WATER,
        supporting_base=SupportingBase.INDIFFERENT
    ), HenssgeRectalResults(
        post_mortem_interval=10.840566030456234,
        confidence_interval=2.8,
        thermal_quotient=0.5813953488372092,
        corrective_factor=0.763
    )),
    # --------------------- User Corrective factor (with condition parameters filled)
    (InputParameters(
        rectal_temperature=30,
        ambient_temperature=20,
        body_mass=80,
        body_condition=BodyCondition.WARMLY,
        environment=EnvironmentType.STILL_WATER,
        supporting_base=SupportingBase.INDIFFERENT,
        user_corrective_factor=0.2
    ), HenssgeRectalResults(
        post_mortem_interval=7.176556562038131,
        confidence_interval=2.8,
        thermal_quotient=0.5813953488372092,
        corrective_factor=0.465
    )),
    # --------------------- User Corrective factor (without condition parameters)
    (InputParameters(
        rectal_temperature=30,
        ambient_temperature=20,
        body_mass=80,
        user_corrective_factor=0.2
    ), HenssgeRectalResults(
        post_mortem_interval=7.176556562038131,
        confidence_interval=2.8,
        thermal_quotient=0.5813953488372092,
        corrective_factor=0.465
    )),
    # --------------------- Error Test
    (InputParameters(
        rectal_temperature=300,
        ambient_temperature=15,
        body_mass=80,
        body_condition=BodyCondition.NAKED,
        environment=EnvironmentType.MOVING_AIR,
        supporting_base=SupportingBase.WET_LEAVES
    ), HenssgeRectalResults(
        error_message="Any Error"
    )),
]


class Test(unittest.TestCase):
    def test_compute(self):
        # Test each case
        for input_parameters, expected_result in data_test:
            # Compute
            results = core.computations.henssge_rectal.compute(input_parameters)

            # Compare
            if expected_result.error_message:
                self.assertTrue(results.error_message, "Error expected\n" + str(input_parameters))
            else:
                self.assertEqual(expected_result.post_mortem_interval, results.post_mortem_interval,
                                 "Bad PostMortemInterval with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.confidence_interval, results.confidence_interval,
                                 "Bad ConfidenceInterval with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.thermal_quotient, results.thermal_quotient,
                                 "Bad ThermalQuotient with following inputs:\n" + str(input_parameters))
                self.assertEqual(expected_result.corrective_factor, results.corrective_factor,
                                 "Bad CorrectiveFactor with following inputs:\n" + str(input_parameters))
