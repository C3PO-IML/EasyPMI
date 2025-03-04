import numpy as np
import warnings
from scipy.optimize import fsolve

from core.computations.common import determine_corrective_factor, compute_thermal_quotient
from core.constants import TEMPERATURE_LIMITS, BODY_MASS_LIMIT, TemperatureLimitsType
from core.input_parameters import InputParameters
from core.output_results import HenssgeRectalResults


# Main computation
def compute(input_parameters) -> HenssgeRectalResults:
    """
    
    Parameters
    ----------
    input_parameters : InputParameters

    Returns
    -------
    HenssgeRectalResults

    """

    # Validate inputs
    input_is_valid, input_error = _validate_input(input_parameters)
    if not input_is_valid:
        return HenssgeRectalResults(error_message=input_error)

    # Determine the combined corrective factor
    corrective_factor = determine_corrective_factor(
        input_parameters.body_condition,
        input_parameters.environment,
        input_parameters.supporting_base,
        input_parameters.user_corrective_factor,
        input_parameters.body_mass
    )

    # Try computation
    try:
        # Compute PMI
        initial_interval = 1.0
        with warnings.catch_warnings():

            warnings.simplefilter("error")

            try:
                pmi = fsolve(
                    _equation,
                    initial_interval,
                    args=(input_parameters.rectal_temperature, input_parameters.ambient_temperature, input_parameters.body_mass * corrective_factor)
                )[0]

            except RuntimeWarning:
                return HenssgeRectalResults(error_message="Convergence error")

        # Compute confidence interval and thermal quotient
        thermal_quotient = compute_thermal_quotient(input_parameters.rectal_temperature, input_parameters.ambient_temperature)
        confidence_interval = _adjust_confidence_interval(thermal_quotient, corrective_factor)

    except ValueError as e:
        return HenssgeRectalResults(error_message=str(e))

    return HenssgeRectalResults(pmi, confidence_interval, thermal_quotient, corrective_factor)


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
    ambient_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.AMBIENT)
    if not input_parameters.ambient_temperature:
        error_message.append(f"The ambient temperature is absent and must be between {ambient_limits[0]}°C and {ambient_limits[1]}°C.")
    elif not (ambient_limits[0] <= input_parameters.ambient_temperature <= ambient_limits[1]):
        error_message.append(
            f"The ambient temperature ({input_parameters.ambient_temperature}°C) is not valid and must be between {ambient_limits[0]}°C and {ambient_limits[1]}°C.")

    rectal_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.RECTAL)
    if not input_parameters.rectal_temperature:
        error_message.append(f"The rectal temperature is absent and must be between {rectal_limits[0]}°C and {rectal_limits[1]}°C.")
    elif not (rectal_limits[0] <= input_parameters.rectal_temperature <= rectal_limits[1]):
        error_message.append(f"The rectal temperature ({input_parameters.rectal_temperature}°C) is not valid and must be between {rectal_limits[0]}°C and {rectal_limits[1]}°C.")

    # Verification of body mass limits
    if not input_parameters.body_mass:
        error_message.append(f"The body mass is absent and must be between {BODY_MASS_LIMIT[0]}kg and {BODY_MASS_LIMIT[1]}kg.")
    elif not (BODY_MASS_LIMIT[0] <= input_parameters.body_mass <= BODY_MASS_LIMIT[1]):
        error_message.append(f"The body mass ({input_parameters.body_mass}kg) is not valid and must be between {BODY_MASS_LIMIT[0]}kg and {BODY_MASS_LIMIT[1]}kg.")

    # Raise error if some values are not valid
    if len(error_message) > 0:
        return False, '\n'.join(error_message)

    # Returns true if everything is valid
    return True, None


# Internal computations
def _adjust_confidence_interval(thermal_quotient: float, corrective_factor: float) -> float:
    """
    Determines the 95% confidence interval for the Henssge equation (not the brain version).

    Parameters
    ----------
    thermal_quotient : float
        Thermal quotient calculated according to the above equation
    corrective_factor : float
        Corrective factor

    Returns
    -------
    float
        Confidence interval in hours
    """
    corrective_factor_not_1 = not np.isclose(corrective_factor, 1.0)

    if 1 > thermal_quotient > 0.5:
        return 2.8
    elif 0.5 > thermal_quotient > 0.3:
        return 4.5 if corrective_factor_not_1 else 3.2
    elif 0.3 > thermal_quotient > 0.2:
        return 7.0 if corrective_factor_not_1 else 4.5
    return 7.0


def _equation(post_mortem_interval: float, rectal_temperature: float, ambient_temperature: float, body_mass: float) -> float:
    """
    Calculates the post-mortem interval according to the Henssge equation from the rectal temperature.

    Parameters
    ----------
    post_mortem_interval : float
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
    thermal_quotient = compute_thermal_quotient(rectal_temperature, ambient_temperature)

    if ambient_temperature <= 23:
        return thermal_quotient - (1.25 * np.exp(-k * post_mortem_interval) - 0.25 * np.exp(-5 * k * post_mortem_interval))
    else:
        return thermal_quotient - (1.11 * np.exp(-k * post_mortem_interval) - 0.11 * np.exp(-10 * k * post_mortem_interval))
