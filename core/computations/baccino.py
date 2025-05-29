import numpy as np
import warnings
from scipy.optimize import fsolve

from core.constants import TemperatureLimitsType, TEMPERATURE_LIMITS
from core.input_parameters import InputParameters
from core.output_results import BaccinoResults


# Main computation
def compute(input_parameters) -> BaccinoResults:
    """
    
    Parameters
    ----------
    input_parameters : InputParameters

    Returns
    -------
    BaccinoResults

    """

    # Validate inputs
    input_is_valid, input_error = _validate_input(input_parameters)
    if not input_is_valid:
        return BaccinoResults(error_message=input_error)

    # Try computation
    try:
        # Compute PMI
        baccino_interval = _equation_interval(input_parameters.tympanic_temperature)
        baccino_global = _equation_global(input_parameters.tympanic_temperature, input_parameters.ambient_temperature)

        # Compute confidence interval
        baccino_confidence_interval = _compute_confidence_interval(baccino_interval)
        baccino_confidence_global = _compute_confidence_interval(baccino_global)

    except ValueError as e:
        return BaccinoResults(error_message=str(e))

    return BaccinoResults(baccino_interval, baccino_global, baccino_confidence_interval, baccino_confidence_global)


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
def _equation_interval(tympanic_temperature: float) -> float:
    """
    This function implements the interval equation developed by Baccino to estimate
    the post-mortem interval (PMI - Post Mortem Interval) from the tympanic.

    Parameters
    ----------
    tympanic_temperature : float
        Measured tympanic temperature on the body (in degrees Celsius).
        The formula is calibrated with an initial temperature of 37°C.

    Returns
    -------
    tuple
        Contains in order:
        - PMI_interval (float): Post-mortem interval in hours according to the interval equation
        - PMI_global (float): Post-mortem interval in hours according to the global equation
        - CI_interval (float): 95% confidence interval for PMI_interval
        - CI_global (float): 95% confidence interval for PMI_global

    Raises
    ------
    ValueError
        If the tympanic temperature is less than or equal to the ambient temperature.
    """
    if tympanic_temperature >= 37:
        raise ValueError("The tympanic temperature must be less than 37°C.")

    return (56.44 * (37.0 - tympanic_temperature) - 150.0) / 60.0


def _equation_global(tympanic_temperature: float, ambient_temperature: float) -> float:
    """
    This function implements the global equation developed by Baccino to estimate
    the post-mortem interval (PMI - Post Mortem Interval) from the tympanic and ambient temperatures.

    Parameters
    ----------
    tympanic_temperature : float
        Measured tympanic temperature on the body (in degrees Celsius).
        The formula is calibrated with an initial temperature of 37°C.
    ambient_temperature : float
        Ambient temperature at the discovery site (in degrees Celsius).

    Returns
    -------
    tuple
        Contains in order:
        - PMI_interval (float): Post-mortem interval in hours according to the interval equation
        - PMI_global (float): Post-mortem interval in hours according to the global equation
        - CI_interval (float): 95% confidence interval for PMI_interval
        - CI_global (float): 95% confidence interval for PMI_global

    Raises
    ------
    ValueError
        If the tympanic temperature is less than or equal to the ambient temperature.
    """
    if tympanic_temperature <= ambient_temperature:
        raise ValueError("Tympanic temperature must be greater than ambient temperature.")
    if tympanic_temperature >= 37:
        raise ValueError("The tympanic temperature must be less than 37°C.")

    return (57.0 * (37.0 - tympanic_temperature) + 6.7 * ambient_temperature - 240.0) / 60.0


def _compute_confidence_interval(post_mortem_interval: float) -> float:
    """
    Computation of the confidence interval
    
    Parameters
    ----------
    post_mortem_interval : float

    Returns
    -------
    float

    """
    return 0.4 * post_mortem_interval
