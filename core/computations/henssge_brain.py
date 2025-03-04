import numpy as np
import warnings
from scipy.optimize import fsolve

from core.computations.common import compute_thermal_quotient
from core.constants import TemperatureLimitsType, TEMPERATURE_LIMITS
from core.input_parameters import InputParameters
from core.output_results import HenssgeBrainResults


# Main computation
def compute(input_parameters) -> HenssgeBrainResults:
    """
    
    Parameters
    ----------
    input_parameters : InputParameters

    Returns
    -------
    HenssgeBrainResults

    """

    # Validate inputs
    input_is_valid, input_error = _validate_input(input_parameters)
    if not input_is_valid:
        return HenssgeBrainResults(error_message=input_error)

    # Try computation
    try:
        # Compute PMI
        initial_interval = 1.0
        with warnings.catch_warnings():

            warnings.simplefilter("error")

            try:
                post_mortem_interval = fsolve(_equation, initial_interval, args=(input_parameters.tympanic_temperature, input_parameters.ambient_temperature))[0]

            except RuntimeWarning:
                return HenssgeBrainResults(error_message="Convergence error")

        # Compute confidence interval
        confidence_interval = _compute_confidence_interval(post_mortem_interval)

    except ValueError as e:
        return HenssgeBrainResults(error_message=str(e))

    return HenssgeBrainResults(post_mortem_interval, confidence_interval)


# Input verifications
def _validate_input(input_parameters: InputParameters) -> tuple:
    """
    Validation of members of input parameters
    
    Parameters
    ----------
    input_parameters : InputParameters        

    Returns
    -------
    bool
        True if inputs are valid
    str
        Human readable error message, or None on success.     
    """

    error_message = []

    # Verification of temperature limits
    tympanic_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.TYMPANIC)
    if not input_parameters.tympanic_temperature:
        error_message.append(f"The tympanic temperature is absent and must be between {tympanic_limits[0]}°C and {tympanic_limits[1]}°C.")
    elif not (tympanic_limits[0] <= input_parameters.tympanic_temperature <= tympanic_limits[1]):
        error_message.append(
            f"The tympanic temperature ({input_parameters.tympanic_temperature}°C) is not valid and must be between {tympanic_limits[0]}°C and {tympanic_limits[1]}°C.")

    ambient_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.AMBIENT)
    if not input_parameters.ambient_temperature:
        error_message.append(f"The ambient temperature is absent and must be between {ambient_limits[0]}°C and {ambient_limits[1]}°C.")
    elif not (ambient_limits[0] <= input_parameters.ambient_temperature <= ambient_limits[1]):
        error_message.append(
            f"The ambient temperature ({input_parameters.ambient_temperature}°C) is not valid and must be between {ambient_limits[0]}°C and {ambient_limits[1]}°C.")

    # Raise error if some values are not valid
    if len(error_message) > 0:
        return False, '\n'.join(error_message)

    # Returns true if everything is valid
    return True, None


# Internal computations
def _compute_confidence_interval(post_mortem_interval: float) -> float:
    """
    Determines the 95% confidence interval for the Henssge equation (brain version).

    Parameters
    ----------
    post_mortem_interval : float
        Estimated post-mortem interval (PMI) in hours

    Returns
    -------
    float
        Confidence interval in hours

    Raises
    ------
    ValueError
        If the post-mortem interval is greater than 13.5 hours, as the method
        becomes significantly less accurate beyond this limit
    """
    if post_mortem_interval <= 6.5:
        return 1.5
    elif 6.5 < post_mortem_interval <= 10.5:
        return 2.5
    elif 10.5 < post_mortem_interval <= 13.5:
        return 3.5
    else:
        raise ValueError("Error: The method becomes less accurate beyond 13.5 hours")


def _equation(post_mortem_interval: float, tympanic_temperature: float, ambient_temperature: float) -> float:
    """
    Calculates the post-mortem interval according to another Henssge equation (variation of the equation for brain temperature) from the tympanic temperature.

    Parameters
    ----------
    post_mortem_interval : float
        Time elapsed since death (Post-Mortem Interval or PMI) in hours
    tympanic_temperature : float
        Measured tympanic temperature in °C
    ambient_temperature : float
        Measured ambient temperature in °C

    Returns
    -------
    float
        Post-mortem interval
    """
    thermal_quotient = compute_thermal_quotient(tympanic_temperature, ambient_temperature)
    return thermal_quotient - (1.135 * np.exp(-0.127 * post_mortem_interval) - 0.135 * np.exp(-1.07 * post_mortem_interval))
