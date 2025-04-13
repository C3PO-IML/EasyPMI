import numpy as np
import warnings
from scipy.optimize import fsolve

from core.constants import BodyCondition, EnvironmentType, SupportingBase, CORRECTIVE_FACTOR, SUPPORTING_BASE_FACTOR, STANDARD_BODY_TEMPERATURE


def compute_thermal_quotient(temperature: float, ambient_temperature: float) -> float:
    """
    
    Parameters
    ----------
    temperature : float
    ambient_temperature : float

    Returns
    -------
    Thermal Quotient : float
    """
    return (temperature - ambient_temperature) / (STANDARD_BODY_TEMPERATURE - ambient_temperature)

def determine_corrective_factor(
        body_condition: BodyCondition,
        environment: EnvironmentType,
        supporting_base: SupportingBase,
        user_corrective_factor: float,
        body_mass: float
) -> float:
    """
    Determines the corrective factor following this sequence:
    1. Checks for manual user input (input_Cf)
    2. If no input_Cf, determines Cf from body_condition and environment
    3. Adds supporting_base factor if applicable
    4. Calculates weight-adjusted corrective factor (Cf_corrige)

    Parameters
    ----------
    body_condition : str
        Body condition (e.g., 'naked', 'lightly dressed', etc.)
    environment : str
        Environment (e.g., 'still air', 'still water', etc.)
    supporting_base : str
        Type of supporting base (e.g., 'Indifferent', 'Heavy padding', etc.)
    user_corrective_factor : float
        Manual user input for corrective factor (default None)
    body_mass : float
        Body mass in kg (default None)

    Returns
    -------
    float
        Final adjusted corrective factor (Cf_corrige)
    """

    corrective_factor = user_corrective_factor

    # If no user input, determine corrective from body_condition and environment
    if not corrective_factor:
        # Handle missing or invalid body_condition
        if body_condition not in CORRECTIVE_FACTOR:
            body_condition = BodyCondition.NOT_SPECIFIED

        # Handle missing or invalid environment
        body_condition_correction_factor = CORRECTIVE_FACTOR.get(body_condition)
        if environment not in body_condition_correction_factor:
            environment = EnvironmentType.NOT_SPECIFIED

        # Get initial corrective factor from predefined table
        corrective_factor = body_condition_correction_factor.get(environment)

        # Add supporting base factor if applicable
        if supporting_base != SupportingBase.INDIFFERENT and supporting_base != SupportingBase.NOT_SPECIFIED and supporting_base in SUPPORTING_BASE_FACTOR:
            corrective_factor += SUPPORTING_BASE_FACTOR.get(supporting_base).get(body_condition, 0.0)

    # Calculate weight-adjusted corrective factor
    corrective_factor = _compute_adjusted_corrective_factor(corrective_factor, body_mass, body_condition, environment, supporting_base)

    return np.round(corrective_factor, 3)

def _compute_adjusted_corrective_factor(corrective_factor: float, body_mass: float, body_condition: BodyCondition, environment: EnvironmentType,
                                        supporting_base: SupportingBase) -> float:
    """
    Calculates the adjusted correction factor based on weight.

    Parameters
    ----------
    corrective_factor : float
        Initial correction factor
    body_mass : float
        Body mass in kg
    body_condition : BodyCondition
    environment : EnvironmentType
    supporting_base : SupportingBase

    Returns
    -------
    float
        Adjusted correction factor
    """

    if corrective_factor == 1.0 or body_mass == 70:
        return corrective_factor
    
    return (-1.2815 / ((body_mass ** -0.625 - 0.0284) * (-3.24596 * np.exp(-0.89959 * corrective_factor)) - 0.0354)) ** 1.6 / body_mass