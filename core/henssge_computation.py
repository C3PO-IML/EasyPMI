import numpy as np
import warnings
from scipy.optimize import fsolve

from core.common_computation import determine_corrective_factor, compute_thermal_quotient
from core.constants import BodyCondition, EnvironmentType, SupportingBase
from core.output_results import HenssgeRectalResults, HenssgeBrainResults

def compute_rectal(input_parameters) -> HenssgeRectalResults:
    """
    
    Parameters
    ----------
    input_parameters

    Returns
    -------

    """
    
    try:
        # Determine the combined corrective factor
        corrective_factor = determine_corrective_factor(
            input_parameters.body_condition,
            input_parameters.environment,
            input_parameters.supporting_base,
            input_parameters.user_corrective_factor,
            input_parameters.body_mass
        )

        # Compute PMI
        t_initial = 1.0
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            try:
                death_time = fsolve(_rectal_equation, t_initial, args=(input_parameters.rectal_temperature, input_parameters.ambient_temperature, input_parameters.body_mass * corrective_factor))[0]
            except RuntimeWarning:
                return HenssgeRectalResults(f"**Henssge Method (Rectal) :**\nConvergence error.\n\n")

        thermal_quotient = compute_thermal_quotient(input_parameters.rectal_temperature, input_parameters.ambient_temperature)
        confidence_interval = _adjust_confidence_interval_rectal(thermal_quotient, corrective_factor_not_equals_1 = (corrective_factor != 1.0))

    except ValueError as e:
        return HenssgeRectalResults(f"**Henssge Method (Rectal) :**\n{e}\n\n")

    return HenssgeRectalResults(death_time, confidence_interval, thermal_quotient)


def compute_brain(input_parameters) -> HenssgeBrainResults:
    """
    
    Parameters
    ----------
    input_parameters

    Returns
    -------

    """
    return HenssgeBrainResults()

def _adjust_confidence_interval_rectal(thermal_quotient: float, corrective_factor_not_equals_1: bool = False) -> float:
    """
    Determines the 95% confidence interval for the Henssge equation (not the brain version).

    Parameters
    ----------
    thermal_quotient : float
        Thermal quotient calculated according to the above equation
    corrective_factor_not_equals_1 : bool, optional
        Indicates whether a corrective_factor other than 1 is applied (default is False)

    Returns
    -------
    float
        Confidence interval in hours
    """
    if 1 > thermal_quotient > 0.5:
        return 2.8
    elif 0.5 > thermal_quotient > 0.3:
        return 4.5 if corrective_factor_not_equals_1 else 3.2
    elif 0.3 > thermal_quotient > 0.2:
        return 7.0 if corrective_factor_not_equals_1 else 4.5
    return 7.0

def _rectal_equation(time_since_death: float, rectal_temperature: float, ambient_temperature: float, body_mass: float) -> float:
    """
    Calculates the post-mortem interval according to the Henssge equation from the rectal temperature.

    Parameters
    ----------
    time_since_death : float
        Time elapsed since death (Post-Mortem Interval or PMI) in hours
    rectal_temperature : float
        Measured rectal temperature in °C
    ambient_temperature : float
        Measured ambient temperature in °C
    body_mass : float
        Body mass in kg

    Returns
    -------
    float
        Post-mortem interval
    """
    k = (1.2815 / body_mass ** 0.625) - 0.0284
    if ambient_temperature <= 23:
        return (rectal_temperature - ambient_temperature) / (37.2 - ambient_temperature) - (1.25 * np.exp(-k * time_since_death) - 0.25 * np.exp(-5 * k * time_since_death))
    else:
        return (rectal_temperature - ambient_temperature) / (37.2 - ambient_temperature) - (1.11 * np.exp(-k * time_since_death) - 0.11 * np.exp(-10 * k * time_since_death))
