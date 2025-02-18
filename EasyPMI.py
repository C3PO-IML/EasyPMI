# This file is part of EasyPMI project.
#
# Post mortem delay claculator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License 3, as published by
# the Free Software Foundation.
#
# Post mortem delay claculator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Post mortem delay claculator. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from scipy.optimize import fsolve
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import math
import warnings
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
import io
import os

# Constants
class TemperatureLimits:
    t_tympanic = (0, 37.5)
    t_rectal = (0, 37.5)
    t_ambient = (-20, 37)

class weightlimit:
    M = (1, 200)

class correctivefactor:
        corrective_factor = {
            'Not specified': {'Not specified': 1.0, 'still air': 1.0, 'moving air': 1.0, 'wet and still air': 1.0, 'wet and moving air': 1.0, 'still water': 1.0, 'flowing water': 1.0},
            'naked': {'Not specified': 1.0, 'still air': 1.0, 'moving air': 0.75, 'wet and still air': 0.7, 'wet and moving air': 0.7, 'still water': 0.5, 'flowing water': 0.35},
            'lightly dressed (one to two thin layers)': {'Not specified': 1.0, 'still air': 1.1, 'moving air': 0.9, 'wet and still air': 0.8, 'wet and moving air': 0.7, 'still water': 0.5, 'flowing water': 0.35},
            'moderately dressed (two to three thin layers)': {'Not specified': 1.0, 'still air': 1.2, 'moving air': 1.0, 'wet and still air': 0.85, 'wet and moving air': 0.75, 'still water': 0.6, 'flowing water': 0.4},
            'warmly dressed (thick layers)': {'Not specified': 1.0, 'still air': 1.4, 'moving air': 1.2, 'wet and still air': 1.1, 'wet and moving air': 0.9, 'still water': 0.7, 'flowing water': 0.5},
            'very dressed (thick blanket)': {'Not specified': 1.0, 'still air': 1.8, 'moving air': 1.4, 'wet and still air': 1.05, 'wet and moving air': 0.95, 'still water': 0.75, 'flowing water': 0.55}
        }

        supporting_base_factors = { 
            'Not specified': 0.0,
            'Indifferent': 0.0,
            'Heavy padding': {
                'naked': 1.3,
                'lightly dressed (one to two thin layers)': 0.3,
                'moderately dressed (two to three thin layers)': 0.2,
                'warmly dressed (thick layers)': 0.1,
                'very dressed (thick blanket)': 0.1
            },
            'Mattress (bed), thick carpet': {
                'naked': 1.1,
                'lightly dressed (one to two thin layers)': 0.1,
                'moderately dressed (two to three thin layers)': 0.1,
                'warmly dressed (thick layers)': 0.1,
                'very dressed (thick blanket)': 0.1
            },
            'About 2 cm wettish leaves': {
                'naked': 1.3,
                'lightly dressed (one to two thin layers)': 0,
                'moderately dressed (two to three thin layers)': 0,
                'warmly dressed (thick layers)': 0,
                'very dressed (thick blanket)': 0
            },
            'About 2 cm totally dry leaves': {
                'naked': 1.5,
                'lightly dressed (one to two thin layers)': 0,
                'moderately dressed (two to three thin layers)': 0,
                'warmly dressed (thick layers)': 0,
                'very dressed (thick blanket)': 0
            },
            'Concrete, stony, tiled': {
                'naked': -0.75,
                'lightly dressed (one to two thin layers)': -0.2,
                'moderately dressed (two to three thin layers)': -0.2,
                'warmly dressed (thick layers)': -0.1,
                'very dressed (thick blanket)': -0.1
            }
        }

# Utility functions

def convert_decimal_separator(value: str) -> float:
    """
    Convert a numeric string with a comma as a decimal separator to a float.
    The function handles various input formats including spaces, multiple commas,
    and different whitespace characters.

    Parameters
    ----------
    value : str
        Input string that may contain a comma as a decimal separator.
    Returns
    -------
    float
        Converted number.
    Raises
    ------
    ValueError
        If the input string is empty or cannot be converted to a float.
    """
    if not value:
        raise ValueError("Input value is empty")
    
    # Clean the input
    value = (
        value
        .strip()                     # Remove leading/trailing whitespace
        .replace('\xa0', ' ')        # Replace non-breaking spaces
        .replace('\t', ' ')          # Replace tabs with spaces
        .replace(' ', '')            # Remove all spaces
    )
    
    # Check for multiple commas
    if value.count(',') > 1:
        raise ValueError(f"Multiple commas found in input: {value}")
    
    # Replace comma with dot
    value = value.replace(',', '.')
    
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number format: {value}")

def format_time(time: float) -> str:
    """
    Formats the time in hours and minutes.

    This function converts a given time into hours and minutes for better readability.

    Parameters
    ----------
    time : float
        Time in hours

    Returns
    -------
    str
        Formatted time in hours and minutes
    """
    if time == float('inf'):
        return "∞"
    hours = int(time)
    minutes = int((time - hours) * 60)
    return f"{hours}h{minutes:02}"

def determine_corrective_factor(body_condition: str, environment: str, supporting_base: str, input_Cf: str = None, M: float = None) -> float:
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
    input_Cf : str, optional
        Manual user input for corrective factor (default None)
    M : float, optional
        Body mass in kg (default None)

    Returns
    -------
    float
        Final adjusted corrective factor (Cf_corrige)
    """
    # Step 1: Check for manual user input
    if input_Cf: 
        if not isinstance(input_Cf, str):
            return None
        try:
            Cf = convert_decimal_separator(input_Cf)
        except:
            return None
    
    # Step 2: If no manual input, determine Cf from body_condition and environment
    else:
        # Handle missing or invalid body_condition
        if body_condition not in correctivefactor.corrective_factor:
            body_condition = 'Not specified'
        
        # Handle missing or invalid environment
        if environment not in correctivefactor.corrective_factor[body_condition]:
            environment = 'Not specified'
            
        # Get initial Cf from predefined table
        Cf = correctivefactor.corrective_factor[body_condition][environment]
        
        # Step 3: Add supporting base factor if applicable
        if supporting_base != "Indifferent" and supporting_base != "Not specified":
            if supporting_base in correctivefactor.supporting_base_factors:
                if isinstance(correctivefactor.supporting_base_factors[supporting_base], dict):
                    Cf += correctivefactor.supporting_base_factors[supporting_base].get(body_condition, 0.0)
    
    # Step 4: Calculate weight-adjusted corrective factor
    if body_condition == "naked" and environment == "still air" and supporting_base == "Indifferent":
        Cf_corrige = 1.0
    else:
        Cf_corrige = calculate_adjusted_Cf(Cf, M)

    return round(Cf_corrige, 3)

def adjust_CI(Q: float, corrective_factor: bool = False) -> float:
    """
    Determines the 95% confidence interval for the Henssge equation (not the brain version).

    Parameters
    ----------
    Q : float
        Thermal quotient calculated according to the above equation
    corrective_factor : bool, optional
        Indicates whether a corrective_factor other than 1 is applied (default is False)

    Returns
    -------
    float
        Confidence interval in hours
    """
    if 1 > Q > 0.5:
        return 2.8
    elif 0.5 > Q > 0.3:
        return 4.5 if corrective_factor else 3.2
    elif 0.3 > Q > 0.2:
        return 7.0 if corrective_factor else 4.5
    return 7.0

def adjust_CI_brain(pmi: float) -> float:
    """
    Determines the 95% confidence interval for the Henssge equation (brain version).

    Parameters
    ----------
    pmi : float
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
    if pmi <= 6.5:
        return 1.5
    elif 6.5 < pmi <= 10.5:
        return 2.5
    elif 10.5 < pmi <= 13.5:
        return 3.5
    else:
        raise ValueError("Error: The method becomes less accurate beyond 13.5 hours")

def calculate_adjusted_Cf(Cf: float, M: float) -> float:
    """
    Calculates the adjusted correction factor based on weight.

    Parameters
    ----------
    Cf : float
        Initial correction factor
    M : float
        Body mass in kg

    Returns
    -------
    float
        Adjusted correction factor
    """
    if Cf is None or M is None:
        return None
        
    # Check if mass is within valid range
    min_mass, max_mass = weightlimit.M
    if not (min_mass <= M <= max_mass):
        return None

    return (-1.2815 / (((M ** -0.625 - 0.0284) * (-3.24596 * math.exp(-0.89959 * Cf)) - 0.0354))) ** 1.6 / M

# Calculation functions
def equation_henssge(t: float, t_rectal: float, t_ambient: float, M: float) -> float:
    """
    Calculates the post-mortem interval according to the Henssge equation from the rectal temperature.

    Parameters
    ----------
    t : float
        Time elapsed since death (Post-Mortem Interval or PMI) in hours
    t_rectal : float
        Measured rectal temperature in °C
    t_ambient : float
        Measured ambient temperature in °C
    M : float
        Body mass in kg

    Returns
    -------
    float
        Post-mortem interval
    """
    k = (1.2815 / M**0.625) - 0.0284
    if t_ambient <= 23:
        residual =  (t_rectal - t_ambient) / (37.2 - t_ambient) - (1.25 * np.exp(-k * t) - 0.25 * np.exp(-5 * k * t))
    else:
        residual = (t_rectal - t_ambient) / (37.2 - t_ambient) - (1.11 * np.exp(-k * t) - 0.11 * np.exp(-10 * k * t))
    return residual

def equation_henssge_brain(t: float, t_tympanic: float, t_ambient: float) -> float:
    """
    Calculates the post-mortem interval according to another Henssge equation (variation of the equation for brain temperature) from the tympanic temperature.

    Parameters
    ----------
    t : float
        Time elapsed since death (= Post-Mortem Interval or PMI) in hours
    t_tympanic : float
        Tympanic temperature in °C
    t_ambient : float
        Ambient temperature in °C

    Returns
    -------
    float
        Post-mortem interval
    """
    residual = (t_tympanic - t_ambient) / (37.2 - t_ambient) - (1.135 * np.exp(-0.127 * t) - 0.135 * np.exp(-1.07 * t))
    return residual

def determine_pmi_with_correction_and_CI_henssge_rectal(t_rectal: float, t_ambient: float, M: float, Cf: float = 1.0) -> tuple:
    """
    Calculates the post-mortem interval with correction and confidence interval according to the Henssge rectal equation.

    Parameters
    ----------
    t_rectal : float
        Measured rectal temperature (in °C)
    t_ambient : float
        Ambient temperature (in °C)
    M : float
        Body mass (in kg)
    Cf : float, optional
        Initial correction factor (default is 1.0 if the body is naked in a still air environment)

    Returns
    -------
    tuple
        Contains in order:
        - t_corrected: Estimated post-mortem interval (in hours)
        - t_min: Lower limit of the confidence interval
        - t_max: Upper limit of the confidence interval
        - Q: Calculated thermal quotient (which should be displayed in the results to facilitate reproducibility)
        - CI: Confidence interval
        - error_message: Error message in case of failure (None if successful)
    """
    # Determine the corrective factor
    Cf_corrige = determine_corrective_factor(
        st.session_state.body_condition,
        st.session_state.environment,
        st.session_state.supporting_base,
        st.session_state.input_Cf,
        M
    )

    M_corrige = M * Cf_corrige
    t_initial = 1.0

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            t_solution = fsolve(equation_henssge, t_initial, args=(t_rectal, t_ambient, M_corrige))
            t_corrige = t_solution[0]
        except RuntimeWarning:
            return None, None, None, None, None, "Convergence error."

    Q = (t_rectal - t_ambient) / (37.2 - t_ambient)
    CI = adjust_CI(Q, corrective_factor=(Cf != 1.0))

    t_min = t_corrige - CI
    t_max = t_corrige + CI
    return t_corrige, t_min, t_max, Q, CI, None

def determine_pmi_and_CI_henssge_brain(t_tympanic: float, t_ambient: float) -> tuple:
    """
    Determines the post-mortem interval using the Henssge brain equation and calculates its confidence interval.

    Parameters
    ----------
    t_tympanic : float
        Measured tympanic temperature on the body (in degrees Celsius).
        Must be a physiologically plausible value (typically between 0°C and 37°C).
    t_ambient : float
        Ambient temperature at the discovery site (in degrees Celsius).

    Returns
    -------
    tuple
        Contains in order:
        - t_corrige (float): Estimated post-mortem interval in hours
        - t_min (float): Lower bound of the confidence interval
        - t_max (float): Upper bound of the confidence interval
        - None: Placeholder for compatibility with other functions
        - CI (float): Confidence interval value
        - error_message (str or None): Error message if failure, None otherwise

    Raises
    ------
    RuntimeWarning
        If the numerical method does not converge to a solution.
    ValueError
        If the input parameters are outside physiological limits or
        if the confidence interval adjustment fails.
    """
    t_initial = 1.0

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            t_solution = fsolve(equation_henssge_brain, t_initial, args=(t_tympanic, t_ambient))
            t_corrige = t_solution[0]
        except RuntimeWarning:
            return None, None, None, None, None, "Convergence error."

    try:
        CI = adjust_CI_brain(t_corrige)
    except ValueError as e:
        return None, None, None, None, None, str(e)

    t_min = t_corrige - CI
    t_max = t_corrige + CI
    return t_corrige, t_min, t_max, None, CI, None

def calculate_baccino(t_tympanic: float, t_ambient: float) -> tuple:
    """
    This function implements the two equations developed by Baccino to estimate
    the post-mortem interval (PMI - Post Mortem Interval) from the tympanic and ambient temperatures.
    Unlike Henssge's equations, these formulas directly provide the result
    without requiring numerical solving. Graphically, this results in a straight line,
    which is not of interest, so I did not create a graph for this function.

    Parameters
    ----------
    t_tympanic : float
        Measured tympanic temperature on the body (in degrees Celsius).
        The formula is calibrated with an initial temperature of 37°C.
    t_ambient : float
        Ambient temperature at the discovery site (in degrees Celsius).
        Used only in the global equation.

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
    if t_tympanic <= t_ambient:
        raise ValueError("Tympanic temperature must be greater than ambient temperature.")
    if t_tympanic >= 37:
        raise ValueError("The tympanic temperature must be less than 37°C.")

    PMI_interval = (56.44 * (37 - t_tympanic) - 150) / 60
    PMI_global = (57 * (37 - t_tympanic) + 6.7 * t_ambient - 240) / 60
    CI_interval = PMI_interval * 0.4
    CI_global = PMI_global * 0.4
    return PMI_interval, PMI_global, CI_interval, CI_global

def estimate_pmi(reaction_type: str, intervals: dict) -> tuple:
    """
    Retrieves the time interval corresponding to a given reaction type.

    This function obtains the temporal bounds (minimum and maximum) associated with
    a specific reaction or sign. These intervals are used to estimate the time
    based on observations.

    Parameters
    ----------
    reaction_type : str
        Identifier or description of the observed reaction or sign type
        (e.g., 'rigor', 'lividity', 'temperature', etc.)

    intervals : dict
        Dictionary containing key-value pairs where:
        - key: reaction type (str)
        - value: tuple (min, max) representing the time interval in hours

    Returns
    -------
    tuple
        A tuple containing (min_time, max_time) in hours.
        If the reaction_type is not found in intervals, returns (0, inf)
    """
    return intervals.get(reaction_type)

# Plotting functions
def plot_temperature_henssge_rectal(t_rectal: float, t_ambient: float, M: float, Cf: float, t_max: float, t_min: float, corrected_pmi: float) -> Figure:
    """
    Plots the post-mortem thermal decay curve according to the Henssge equation.

    This function generates a Matplotlib plot representing the evolution of the
    rectal temperature over time, based on the Henssge model for rectal temperature.
    The plot includes the theoretical curve, the current measurement point, and the
    confidence interval.

    Parameters
    ----------
    t_rectal : float
        Measured rectal temperature (in °C).
    t_ambient : float
        Ambient temperature (in °C).
    M : float
        Body mass (in kg).
    Cf : float
        Raw correction factor (before mass adjustment).
    t_max : float
        Upper bound of the confidence interval (in hours).
    t_min : float
        Lower bound of the confidence interval (in hours).
    corrected_pmi : float
        Estimated corrected post-mortem interval (in hours).

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    max_time = 50
    time = np.linspace(0, max_time, 100)

    # Determine the combined corrective factor
    Cf_corrige = determine_corrective_factor(
        st.session_state.body_condition,
        st.session_state.environment,
        st.session_state.supporting_base,
        st.session_state.input_Cf,
        M
    )

    M_corrige = M * Cf_corrige
    temperatures = []

    for t in time:
        if t_ambient <= 23:
            temperatures.append(t_ambient + (37.2 - t_ambient) * (1.25 * np.exp(-(1.2815 / M_corrige**0.625 - 0.0284) * t) - 0.25 * np.exp(-5 * (1.2815 / M_corrige**0.625 - 0.0284) * t)))
        else:
            temperatures.append(t_ambient + (37.2 - t_ambient) * (1.11 * np.exp(-(1.2815 / M_corrige**0.625 - 0.0284) * t) - 0.11 * np.exp(-10 * (1.2815 / M_corrige**0.625 - 0.0284) * t)))

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=t_rectal, color='r', linestyle='--', label=f"Current temperature: {t_rectal} °C")
    ax.scatter(corrected_pmi, t_rectal, color='b', label=f"Estimated time: {format_time(corrected_pmi)}")

    ax.axvspan(t_min, t_max, color='green', alpha=0.3, label=f"CI: {format_time(t_min)} - {format_time(t_max)}")

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Rectal temperature (°C)")
    ax.set_title("Evolution of rectal temperature", fontsize=12)

    ax.legend(loc='upper right', bbox_to_anchor=(1, 1), prop={'size': 8}, fancybox=True, shadow=True)
    ax.grid(True)

    return fig

def plot_temperature_henssge_brain(t_tympanic: float, t_ambient: float, t_max: float, t_min: float, corrected_pmi: float) -> Figure:
    """
    Plots the post-mortem brain thermal decay curve according to the Henssge equation.

    This function generates a Matplotlib plot representing the evolution of the
    tympanic temperature (an indicator of brain temperature) over time. The model
    uses a specific Henssge equation for brain cooling, which differs from the one
    used for rectal temperature in its constants and simplified form (no dependence
    on body mass).

    Parameters
    ----------
    t_tympanic : float
        Measured tympanic temperature (in °C).
    t_ambient : float
        Ambient temperature (in °C).
    t_max : float
        Upper bound of the confidence interval (in hours).
    t_min : float
        Lower bound of the confidence interval (in hours).
    corrected_pmi : float
        Estimated corrected post-mortem interval (in hours).

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    max_time = 50
    time = np.linspace(0, max_time, 100)
    temperatures = [t_ambient + (37.2 - t_ambient) * (1.135 * np.exp(-0.127 * t) - 0.135 * np.exp(-1.07 * t)) for t in time]

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=t_tympanic, color='r', linestyle='--', label=f"Current temperature : {t_tympanic} °C")
    ax.scatter(corrected_pmi, t_tympanic, color='b', label=f"Estimated time : {format_time(corrected_pmi)}")

    ax.axvspan(t_min, t_max, color='green', alpha=0.3, label=f"CI : {format_time(t_min)} - {format_time(t_max)}")

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Tympanic temperature (°C)")
    ax.set_title("Evolution of tympanic temperature", fontsize=12)

    ax.legend(loc='upper right', bbox_to_anchor=(1, 1), prop={'size': 8}, fancybox=True, shadow=True)
    ax.grid(True)

    return fig

def hybrid_scale(x, threshold=20, compression_factor=8):
    """
    Custom hybrid scale transformation.
    Values below the threshold are linear, values above are compressed.
    """
    return np.where(x <= threshold, x, threshold + (x - threshold) / compression_factor)

def inverse_hybrid_scale(x, threshold=20, compression_factor=8):
    """
    Inverse of the hybrid scale transformation.
    """
    return np.where(x <= threshold, x, threshold + (x - threshold) * compression_factor)

def plot_comparative_pmi_results(corrected_pmi: float, t_min: float, t_max: float, corrected_pmi_brain: float, t_min_brain: float, t_max_brain: float, PMI_interval: float, PMI_global: float, CI_interval: float, CI_global: float, pmi_idiomuscular_reaction_min: float, pmi_idiomuscular_reaction_max: float, pmi_rigor_min: float, pmi_rigor_max: float, pmi_lividity_min: float, pmi_lividity_max: float, pmi_lividity_disappearance_min: float, pmi_lividity_disappearance_max: float, pmi_lividity_mobility_min: float, pmi_lividity_mobility_max: float) -> Figure:
    """
    Plots a comparative graph of different post-mortem interval (PMI) estimations.

    This function generates a comparative visualization of different PMI estimation methods,
    including the Henssge method, the Baccino method, and thanatological signs (rigor, lividity, etc.).

    Parameters
    ----------
    corrected_pmi : float or None
        Corrected PMI estimation according to Henssge (in hours)
    t_min : float or None
        Lower bound of the confidence interval for the Henssge estimation
    t_max : float or None
        Upper bound of the confidence interval for the Henssge estimation
    corrected_pmi_brain : float or None
        Corrected PMI estimation based on brain temperature
    t_min_brain : float or None
        Lower bound of the confidence interval for the brain estimation
    t_max_brain : float or None
        Upper bound of the confidence interval for the brain estimation
    PMI_interval : float or None
        PMI estimation according to the Baccino method (interval)
    PMI_global : float or None
        PMI estimation according to the Baccino method (global)
    CI_interval : float or None
        Confidence interval for the Baccino estimation (interval)
    CI_global : float or None
        Confidence interval for the Baccino estimation (global)
    pmi_idiomuscular_reaction_min : float or None
        Lower bound of the estimation based on idiomuscular contraction
    pmi_idiomuscular_reaction_max : float or None
        Upper bound of the estimation based on idiomuscular contraction
    pmi_rigor_min : float or None
        Lower bound of the estimation based on cadaveric rigidity
    pmi_rigor_max : float or None
        Upper bound of the estimation based on cadaveric rigidity
    pmi_lividity_min : float or None
        Lower bound of the estimation based on cadaveric lividity
    pmi_lividity_max : float or None
        Upper bound of the estimation based on cadaveric lividity
    pmi_lividity_disappearance_min : float or None
        Lower bound for the complete disappearance of lividity
    pmi_lividity_disappearance_max : float or None
        Upper bound for the complete disappearance of lividity
    pmi_lividity_mobility_min : float or None
        Lower bound of the estimation based on lividity mobility
    pmi_lividity_mobility_max : float or None
        Upper bound of the estimation based on lividity mobility

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """
    fig = Figure(figsize=(18, 5), dpi=120)
    ax = fig.add_subplot(111)

    def add_vertical_bars(ax: plt.Axes, x1: float, x2: float, y: float, color: str) -> float:
        bar_height = 0.05
        ax.plot([x1, x1], [y - bar_height, y + bar_height], color=color, lw=2)
        ax.plot([x2, x2], [y - bar_height, y + bar_height], color=color, lw=2)
        return bar_height

    def add_interval_values(ax: plt.Axes, x1: float, x2: float, y: float, bar_height: float, color: str) -> None:
        ax.text(x1, y - bar_height - 0.03, f"{format_time(x1)}", ha='center', va='top', fontsize=10, color=color)
        ax.text(x2, y - bar_height - 0.03, f"{format_time(x2)}", ha='center', va='top', fontsize=10, color=color)

    # Create Custom Graduations
    ticks = list(range(0, 21, 4))
    values = [v for v in [t_max, t_max_brain, PMI_interval, PMI_global, pmi_idiomuscular_reaction_max, pmi_rigor_max, pmi_lividity_max, pmi_lividity_disappearance_max, pmi_lividity_mobility_max] if v is not None]
    if CI_interval is not None:
        values.append(PMI_interval + CI_interval)
    if CI_global is not None:
        values.append(PMI_global + CI_global)
    max_value = max(values) if values else 0

    if max_value <= 20:
        ticks = list(range(0, int(max_value) + 1, 4))
    else:
        log_ticks = [30, 40, 50, 60, 80, 100]  # create logarithmic graduations after 20h
        ticks.extend([t for t in log_ticks if t <= max_value])

    # Determine max value for the x-axis
    default_max = 10  # defaut value for the x-axis 
    max_value = max(max(values) if values else default_max, default_max)

    # Apply a custom transformation to the x-axis
    ax.set_xscale('function', functions=(hybrid_scale, inverse_hybrid_scale))

    if corrected_pmi is not None and t_min is not None and t_max is not None:
        ax.errorbar([corrected_pmi], [0], xerr=[[corrected_pmi - t_min], [t_max - corrected_pmi]], fmt='o', color='blue')
        ax.text(corrected_pmi, 0, f"{format_time(corrected_pmi)}", ha='center', va='bottom', fontsize=8)
        bar_height = add_vertical_bars(ax, t_min, t_max, 0, 'blue')
        add_interval_values(ax, t_min, t_max, 0, bar_height, 'blue')

    if corrected_pmi_brain is not None and t_min_brain is not None and t_max_brain is not None:
        ax.errorbar([corrected_pmi_brain], [1], xerr=[[corrected_pmi_brain - t_min_brain], [t_max_brain - corrected_pmi_brain]], fmt='o', color='purple')
        ax.text(corrected_pmi_brain, 1, f"{format_time(corrected_pmi_brain)}", ha='center', va='bottom', fontsize=8)
        bar_height = add_vertical_bars(ax, t_min_brain, t_max_brain, 1, 'purple')
        add_interval_values(ax, t_min_brain, t_max_brain, 1, bar_height, 'purple')

    if PMI_interval is not None and CI_interval is not None:
        ax.errorbar([PMI_interval], [2], xerr=[[CI_interval], [CI_interval]], fmt='o', color='green')
        ax.text(PMI_interval, 2, f"{format_time(PMI_interval)}", ha='center', va='bottom', fontsize=8)
        bar_height = add_vertical_bars(ax, PMI_interval - CI_interval, PMI_interval + CI_interval, 2, 'green')
        add_interval_values(ax, PMI_interval - CI_interval, PMI_interval + CI_interval, 2, bar_height, 'green')

    if PMI_global is not None and CI_global is not None:
        ax.errorbar([PMI_global], [3], xerr=[[CI_global], [CI_global]], fmt='o', color='red')
        ax.text(PMI_global, 3, f"{format_time(PMI_global)}", ha='center', va='bottom', fontsize=8)
        bar_height = add_vertical_bars(ax, PMI_global - CI_global, PMI_global + CI_global, 3, 'red')
        add_interval_values(ax, PMI_global - CI_global, PMI_global + CI_global, 3, bar_height, 'red')

    if pmi_idiomuscular_reaction_min is not None and pmi_idiomuscular_reaction_max is not None:
        if pmi_idiomuscular_reaction_max == 3:
            ax.axvspan(3, max_value, color='gray', alpha=0.5)
            ax.axvline(x=3, color='purple', linestyle='--', lw=2)
            ax.text(3, 4, f"PMI < {format_time(3)}", ha='right', va='bottom', fontsize=8, color='purple')
        elif pmi_idiomuscular_reaction_max == 5.5:
            ax.axvspan(5.5, max_value, color='gray', alpha=0.5)
            ax.axvline(x=5.5, color='purple', linestyle='--', lw=2)
            ax.text(5.5, 4, f"PMI < {format_time(5.5)}", ha='right', va='bottom', fontsize=8, color='purple')
        elif pmi_idiomuscular_reaction_max == float('inf'):
            ax.axvspan(0, 1.5, color='gray', alpha=0.5)
            ax.axvline(x=1.5, color='purple', linestyle='--', lw=2)
            ax.text(1.5, 4, f"PMI > {format_time(1.5)}", ha='left', va='bottom', fontsize=8, color='purple')
        else:
            ax.errorbar([(pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2], [4], xerr=[[(pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2 - pmi_idiomuscular_reaction_min], [pmi_idiomuscular_reaction_max - (pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2]], fmt='none', color='purple')
            bar_height = add_vertical_bars(ax, pmi_idiomuscular_reaction_min, pmi_idiomuscular_reaction_max, 4, 'purple')
            add_interval_values(ax, pmi_idiomuscular_reaction_min, pmi_idiomuscular_reaction_max, 4, bar_height, 'purple')

    if pmi_rigor_min is not None and pmi_rigor_max is not None:
        if pmi_rigor_max == float('inf'):
            ax.axvspan(0, 24, color='gray', alpha=0.5)
            ax.axvline(x=24, color='orange', linestyle='--', lw=2)
            ax.text(24, 5, f"PMI > {format_time(24)}", ha='left', va='bottom', fontsize=8, color='orange')
        elif pmi_rigor_max == 7:
            ax.axvspan(7, max_value, color='gray', alpha=0.5)
            ax.axvline(x=7, color='orange', linestyle='--', lw=2)
            ax.text(7, 5, f"PMI < {format_time(7)}", ha='right', va='bottom', fontsize=8, color='orange')
        else:
            ax.errorbar([(pmi_rigor_min + pmi_rigor_max) / 2], [5], xerr=[[(pmi_rigor_min + pmi_rigor_max) / 2 - pmi_rigor_min], [pmi_rigor_max - (pmi_rigor_min + pmi_rigor_max) / 2]], fmt='none', color='orange')
            bar_height = add_vertical_bars(ax, pmi_rigor_min, pmi_rigor_max, 5, 'orange')
            add_interval_values(ax, pmi_rigor_min, pmi_rigor_max, 5, bar_height, 'orange')

    if pmi_lividity_min is not None and pmi_lividity_max is not None:
        if pmi_lividity_max == float('inf'):
            ax.axvspan(0, 3, color='gray', alpha=0.5)
            ax.axvline(x=3, color='brown', linestyle='--', lw=2)
            ax.text(3, 6, f"PMI > {format_time(3)}", ha='left', va='bottom', fontsize=8, color='brown')
        elif pmi_lividity_min == 0 and pmi_lividity_max == 3:
            ax.axvspan(3, max_value, color='gray', alpha=0.5)
            ax.axvline(x=3, color='brown', linestyle='--', lw=2)
            ax.text(3, 6, f"PMI < {format_time(3)}", ha='right', va='bottom', fontsize=8, color='brown')
        else:
            ax.errorbar([(pmi_lividity_min + pmi_lividity_max) / 2], [6], xerr=[[(pmi_lividity_min + pmi_lividity_max) / 2 - pmi_lividity_min], [pmi_lividity_max - (pmi_lividity_min + pmi_lividity_max) / 2]], fmt='none', color='brown')
            bar_height = add_vertical_bars(ax, pmi_lividity_min, pmi_lividity_max, 6, 'brown')
            add_interval_values(ax, pmi_lividity_min, pmi_lividity_max, 6, bar_height, 'brown')

    if pmi_lividity_disappearance_min is not None and pmi_lividity_disappearance_max is not None:
        if pmi_lividity_disappearance_max == float('inf'):
            ax.axvspan(0, 10, color='gray', alpha=0.5)
            ax.axvline(x=10, color='orange', linestyle='--', lw=2)
            ax.text(10, 7, f"PMI > {format_time(10)}", ha='left', va='bottom', fontsize=8, color='orange')
        else:
            ax.axvspan(20, max_value, color='gray', alpha=0.5)
            ax.axvline(x=20, color='orange', linestyle='--', lw=2)
            ax.text(20, 7, f"PMI < {format_time(20)}", ha='right', va='bottom', fontsize=8, color='orange')

    if pmi_lividity_mobility_min is not None and pmi_lividity_mobility_max is not None:
        if pmi_lividity_mobility_max == float('inf'):
            ax.axvspan(0, 10, color='gray', alpha=0.5)
            ax.axvline(x=10, color='magenta', linestyle='--', lw=2)
            ax.text(10, 8, f"PMI > {format_time(10)}", ha='left', va='bottom', fontsize=8, color='magenta')
        elif pmi_lividity_mobility_max == 6:
            ax.axvspan(6, max_value, color='gray', alpha=0.5)
            ax.axvline(x=6, color='magenta', linestyle='--', lw=2)
            ax.text(6, 8, f"PMI < {format_time(6)}", ha='right', va='bottom', fontsize=8, color='magenta')
        else:
            ax.errorbar([(pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2], [8], xerr=[[(pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2 - pmi_lividity_mobility_min], [pmi_lividity_mobility_max - (pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2]], fmt='none', color='magenta')
            bar_height = add_vertical_bars(ax, pmi_lividity_mobility_min, pmi_lividity_mobility_max, 8, 'magenta')
            add_interval_values(ax, pmi_lividity_mobility_min, pmi_lividity_mobility_max, 8, bar_height, 'magenta')

    ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_yticklabels(['Henssge (Rectal)', 'Henssge (Brain)', 'Baccino\n(Interval)', 'Baccino\n(Global)', 'Idiomuscular\nreaction', 'Rigor', 'Lividity', 'Lividity\n(Disappearance)', 'Lividity\n(Mobility)'])
    ax.set_ylabel('Method', labelpad=10)
    ax.set_xlabel('Estimated Post-Mortem Interval (hours)')
    ax.set_title('Comparison of Estimated Post-Mortem Intervals', pad=10)

    fig.subplots_adjust(left=0.18, bottom=0.15, top=0.9, right=0.92)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=-0.5, top=8.5)
    ax.grid(True, alpha=0.3)

    # Adjust label sizes to optimize space
    ax.tick_params(axis='y', labelsize=9)
    ax.tick_params(axis='x', labelsize=8)

    # Optimize the display of values on the graph
    for text in ax.texts:
        text.set_fontsize(10)

    return fig

# User interface management functions
def reset() -> None:
    """
    Resets all fields in the user interface.
    This function clears all user inputs and resets the graphs.
    """
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reset figures
    st.session_state.fig_henssge = None
    st.session_state.fig_henssge_brain = None
    st.session_state.fig_comparison = None
    st.success("The application has been successfully reset.")
    
    # Force page rerun to reset all widgets
    st.rerun()

def calculate_results() -> None:
    """
    Calculates and displays the results using different methods for estimating the post-mortem interval (PMI).

    This function retrieves the values entered by the user, performs the necessary calculations,
    and displays the results in the user interface. It also handles errors and warnings in case of
    missing or unusable values. The threshold values and ranges are taken from the book "Time of Death"
    by Madea.

    The function uses the following methods to estimate the PMI:
    - Henssge Method (Rectal)
    - Henssge Method (Brain)
    - Baccino Method
    - Idiomuscular Reaction
    - Rigor Mortis
    - Livor Mortis
    - Disappearance of Livor Mortis
    - Livor Mortis Mobility

    The results are displayed in a structured format, and any errors encountered during the calculations
    are reported to the user. Additionally, the function generates and stores plots for visualizing
    the temperature-based methods (Henssge Rectal and Brain) and a comparative plot of all PMI estimates.
    """
    try:
        # Reset figures
        st.session_state.fig_henssge = None
        st.session_state.fig_henssge_brain = None
        st.session_state.fig_comparison = None

        # Get and convert input.values
        t_tympanic = convert_decimal_separator(st.session_state.input_t_tympanic) if st.session_state.input_t_tympanic else None
        t_rectal = convert_decimal_separator(st.session_state.input_t_rectal) if st.session_state.input_t_rectal else None
        t_ambient = convert_decimal_separator(st.session_state.input_t_ambient) if st.session_state.input_t_ambient else None
        M = convert_decimal_separator(st.session_state.input_M) if st.session_state.input_M else None
        idiomuscular_reaction_type = st.session_state.idiomuscular_reaction
        rigor_type = st.session_state.rigor
        lividity_type = st.session_state.lividity
        lividity_disappearance = st.session_state.lividity_disappearance
        lividity_mobility_type = st.session_state.lividity_mobility
        body_condition = st.session_state.body_condition
        environment = st.session_state.environment
        supporting_base = st.session_state.supporting_base

        # Verification of prerequisites for the rectal Henssge equation
        corrected_pmi = None
        t_min = None
        t_max = None
        Q = None
        CI = None
        error_henssge = None
        Cf_corrige = None

        results_henssge = ""

        if t_rectal is None or t_ambient is None or M is None:
            results_henssge = "**Henssge Method (Rectal) :**\n" \
                            "Missing value to perform calculation.\n\n"
        else:
            try:
                # Verification of temperature limits
                if not (TemperatureLimits.t_ambient[0] <= t_ambient <= TemperatureLimits.t_ambient[1]):
                    raise ValueError(f"The ambient temperature must be between {TemperatureLimits.t_ambient[0]} and {TemperatureLimits.t_ambient[1]}°C.")
                if not (TemperatureLimits.t_rectal[0] <= t_rectal <= TemperatureLimits.t_rectal[1]):
                    raise ValueError(f"The rectal temperature must be between {TemperatureLimits.t_rectal[0]} and {TemperatureLimits.t_rectal[1]}°C.")            
                # Verification of weight limits
                if not (weightlimit.M[0] <= M <= weightlimit.M[1]):
                    raise ValueError(f"The body mass must be between {weightlimit.M[0]} and {weightlimit.M[1]} kg.")

                # Determine the combined corrective factor
                Cf_corrige = determine_corrective_factor(
                    body_condition,
                    environment,
                    supporting_base,
                    st.session_state.input_Cf,
                    M
                )

                corrected_pmi, t_min, t_max, Q, CI, error_henssge = determine_pmi_with_correction_and_CI_henssge_rectal(t_rectal, t_ambient, M, Cf_corrige)
                if corrected_pmi is not None:
                    results_henssge = f"**Henssge Method (Rectal) :**\n" \
                                    f"Estimated time since death: {format_time(corrected_pmi)} [{format_time(t_min)} - {format_time(t_max)}]  \n" \
                                    f"Calculated Q: {Q:.2f} (CI {CI:.2f})  \n" \
                                    f"Corrected Cf: {Cf_corrige:.2f}\n\n"
                    st.session_state.fig_henssge = plot_temperature_henssge_rectal(t_rectal, t_ambient, M, Cf_corrige, t_max, t_min, corrected_pmi)
                else:
                    results_henssge = f"**Henssge Method (Rectal) :**\n" \
                                    f"{error_henssge if error_henssge else 'Error in calculation.'}\n\n"
            
            except ValueError as e:
                results_henssge = f"**Henssge Method (Rectal) :**\n" \
                                  f"{e}\n\n"
        
        results_henssge_brain = ""

        corrected_pmi_brain = None
        t_min_brain = None
        t_max_brain = None
        Q_Brain = None
        CI_Brain = None
        error_henssge_brain = None
        if t_tympanic is None or t_ambient is None :
            results_henssge_brain = "**Henssge Method (Brain) :**\n" \
                            "Missing value to perform calculation.\n\n"
        else:
            try:
                # Verification of temperature limits
                if t_tympanic is not None and not (TemperatureLimits.t_tympanic[0] <= t_tympanic <= TemperatureLimits.t_tympanic[1]):
                    raise ValueError(f"The tympanic temperature must be between {TemperatureLimits.t_tympanic[0]} and {TemperatureLimits.t_tympanic[1]}°C.")    
                if t_ambient is not None and not (TemperatureLimits.t_ambient[0] <= t_ambient <= TemperatureLimits.t_ambient[1]):
                    raise ValueError(f"The ambient temperature must be between {TemperatureLimits.t_ambient[0]} and {TemperatureLimits.t_ambient[1]}°C.")
            
                corrected_pmi_brain, t_min_brain, t_max_brain, Q_Brain, CI_Brain, error_henssge_brain = determine_pmi_and_CI_henssge_brain(t_tympanic, t_ambient)
                if corrected_pmi_brain is not None:
                    results_henssge_brain = f"**Henssge Method (Brain) :**\n" \
                                                f"Estimated time since death : {format_time(corrected_pmi_brain)} [{format_time(t_min_brain)} - {format_time(t_max_brain)}]  \n" \
                                                f"CI : {CI_Brain:.2f}\n\n"
                    st.session_state.fig_henssge_brain = plot_temperature_henssge_brain(t_tympanic, t_ambient, t_max_brain, t_min_brain, corrected_pmi_brain)
                elif error_henssge_brain:
                    results_henssge_brain = f"**Henssge Method (Brain) :**\n" \
                                            f"{error_henssge_brain}\n\n"
                else:
                    results_henssge_brain = "**Henssge Method (Brain) :**\n" \
                                            "Missing values to perform the calculation.\n\n"
        
            except ValueError as e:
                results_henssge_brain = f"**Henssge Method (Brain) :**\n" \
                                        f"{e}\n\n"
    
        results_baccino = ""

        PMI_interval = None
        PMI_global = None
        CI_interval = None
        CI_global = None
        if t_tympanic is not None and t_ambient is not None:
            try:
                # Verification of temperature limits
                if t_tympanic is not None and not (TemperatureLimits.t_tympanic[0] <= t_tympanic <= TemperatureLimits.t_tympanic[1]):
                    raise ValueError(f"The tympanic temperature must be between {TemperatureLimits.t_tympanic[0]} and {TemperatureLimits.t_tympanic[1]}°C.")    
                if t_ambient is not None and not (TemperatureLimits.t_ambient[0] <= t_ambient <= TemperatureLimits.t_ambient[1]):
                    raise ValueError(f"The ambient temperature must be between {TemperatureLimits.t_ambient[0]} and {TemperatureLimits.t_ambient[1]}°C.")

                PMI_interval, PMI_global, CI_interval, CI_global = calculate_baccino(t_tympanic, t_ambient)
                results_baccino = f"**Baccino Method :**  \n" \
                                  f"Estimated time since death (Interval) : {format_time(PMI_interval)} [{format_time(PMI_interval - CI_interval)} - {format_time(PMI_interval + CI_interval)}]  \n" \
                                  f"Estimated time since death (Global) : {format_time(PMI_global)} [{format_time(PMI_global - CI_global)} - {format_time(PMI_global + CI_global)}]\n\n"
            except ValueError as e:
                results_baccino = f"**Baccino Method :**\n" \
                                  f"{e}\n\n"
        else:
            results_baccino = "**Baccino Method :**\n" \
                               "Missing values to perform the calculation.\n\n"

        pmi_idiomuscular_reaction_min = None
        pmi_idiomuscular_reaction_max = None
        if idiomuscular_reaction_type and idiomuscular_reaction_type != "Not specified":
            pmi_idiomuscular_reaction_min, pmi_idiomuscular_reaction_max = estimate_pmi(idiomuscular_reaction_type, {
                'zsako': (0, 3),
                'strong reversible': (0, 5.5),
                'weak persistent': (1.5, 13),
                'no reaction': (1.5, float('inf'))
            })
            if idiomuscular_reaction_type == 'no reaction':
                results_idiomuscular_reaction = f"**Idiomuscular Reaction :**\n" \
                                          f"Estimated PMI > {format_time(pmi_idiomuscular_reaction_min)}\n\n"
            else:
                results_idiomuscular_reaction = f"**Idiomuscular Reaction :**\n" \
                                          f"Estimated PMI between {format_time(pmi_idiomuscular_reaction_min)} et {format_time(pmi_idiomuscular_reaction_max)}\n\n"
        else:
            results_idiomuscular_reaction = "**Idiomuscular Reaction :**\n" \
                                      "Not specified.\n\n"

        pmi_rigor_min = None
        pmi_rigor_max = None
        if rigor_type and rigor_type != "Not specified":
            pmi_rigor_min, pmi_rigor_max = estimate_pmi(rigor_type, {
                'Rigidity not established': (0, 7),
                'Possible re-establishment': (0.5, 9.5),
                'Complete rigidity': (2, 20),
                'Persistence': (24, 96),
                'Resolution': (24, float('inf'))
            })
            if rigor_type == 'Resolution':
                results_rigor = f"**Rigor :**\n" \
                                    f"Estimated PMI > {format_time(pmi_rigor_min)}\n\n"
            elif rigor_type == 'Rigidity not established':
                results_rigor = f"**Rigor :**\n" \
                                    f"Estimated PMI < {format_time(pmi_rigor_max)}\n\n"
            else:
                results_rigor = f"**Rigor :**\n" \
                                    f"Estimated PMI between {format_time(pmi_rigor_min)} et {format_time(pmi_rigor_max)}\n\n"
        else:
            results_rigor = "**Rigor :**\n" \
                                "Not specified.\n\n"

        pmi_lividity_min = None
        pmi_lividity_max = None
        if lividity_type and lividity_type != "Not specified":
            pmi_lividity_min, pmi_lividity_max = estimate_pmi(lividity_type, {
                'Absent': (0, 3),
                'Development': (0.25, 3),
                'Confluence': (1, 4),
                'Maximum': (3, float('inf'))
            })
            if pmi_lividity_max == float('inf'):
                results_lividity = f"**Lividity :**\n" \
                                    f"Estimated PMI > {format_time(pmi_lividity_min)}\n\n"
            else:
                results_lividity = f"**Lividity :**\n" \
                                    f"Estimated PMI between {format_time(pmi_lividity_min)} et {format_time(pmi_lividity_max)}\n\n"
        else:
            results_lividity = "**Lividity :**\n" \
                                "Not specified.\n\n"

        pmi_lividity_disappearance_min = None
        pmi_lividity_disappearance_max = None
        if lividity_disappearance and lividity_disappearance != "Not specified":
            pmi_lividity_disappearance_min, pmi_lividity_disappearance_max = estimate_pmi(lividity_disappearance, {
                'Complete disappearance': (0, 20),
                'Incomplete disappearence': (10, float('inf'))
            })
            if pmi_lividity_disappearance_max == float('inf'):
                results_lividity_disappearance = f"**Disappearance of Lividity :**\n" \
                                    f"Estimated PMI > {format_time(pmi_lividity_disappearance_min)}\n\n"
            else:
                results_lividity_disappearance = f"**Disappearance of Lividity :**\n" \
                                    f"Estimated PMI < {format_time(pmi_lividity_disappearance_max)}\n\n"
        else:
            results_lividity_disappearance = "**Disappearance of Lividity :**\n" \
                                "Not specified.\n\n"

        pmi_lividity_mobility_min = None
        pmi_lividity_mobility_max = None
        if lividity_mobility_type and lividity_mobility_type != "Not specified":
            pmi_lividity_mobility_min, pmi_lividity_mobility_max = estimate_pmi(lividity_mobility_type, {
                'Complete': (0, 6),
                'Partial': (4, 24),
                'Only little pallor': (10, float('inf'))
            })
            if pmi_lividity_mobility_max == float('inf'):
                results_lividity_mobility = f"**Lividity Mobility :**\n" \
                                              f"Estimated PMI > {format_time(pmi_lividity_mobility_min)}\n\n"
            else:
                results_lividity_mobility = f"**Lividity Mobility :**\n" \
                                              f"Estimated PMI between {format_time(pmi_lividity_mobility_min)} et {format_time(pmi_lividity_mobility_max)}\n\n"
        else:
            results_lividity_mobility = "**Lividity Mobility :**\n" \
                                          "Not specified.\n\n"

        st.session_state.results = results_henssge + results_henssge_brain + results_baccino + results_idiomuscular_reaction + results_rigor + results_lividity + results_lividity_disappearance + results_lividity_mobility
        st.session_state.fig_comparison = plot_comparative_pmi_results(corrected_pmi, t_min, t_max, corrected_pmi_brain, t_min_brain, t_max_brain, PMI_interval, PMI_global, CI_interval, CI_global, pmi_idiomuscular_reaction_min, pmi_idiomuscular_reaction_max, pmi_rigor_min, pmi_rigor_max, pmi_lividity_min, pmi_lividity_max, pmi_lividity_disappearance_min, pmi_lividity_disappearance_max, pmi_lividity_mobility_min, pmi_lividity_mobility_max)

    except ValueError as e:
        st.session_state.results = f"Error : {e}"

# Function to save results in PDF format
def generate_pdf() -> bytes:
    """
    Generates a PDF in memory and returns the bytes.
    """
    buffer = io.BytesIO()
    width, height = letter
    c = pdf_canvas.Canvas(buffer, pagesize=letter)

    def draw_formatted_text(text, x, y, is_bold=False):
        """Helper function to draw text with proper formatting"""
        if is_bold:
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 12)
        c.drawString(x, y, text.strip('*'))  # Remove any remaining * characters
    
    # Page 1: Title and data
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Post-Mortem Interval Calculation Results")

    # Calculate text width and height for user inputs
    c.setFont("Helvetica", 10)
    user_inputs = [
        f"Tympanic temperature : {st.session_state.input_t_tympanic or 'Not specified'} °C",
        f"Rectal temperature : {st.session_state.input_t_rectal or 'Not specified'} °C", 
        f"Ambient temperature : {st.session_state.input_t_ambient or 'Not specified'} °C",
        f"Body weight : {st.session_state.input_M or 'Not specified'} kg",
        f"Corrective factor : {st.session_state.input_Cf or 'Not specified'}",
        f"Body condition : {st.session_state.body_condition or 'Not specified'}",
        f"Environment : {st.session_state.environment or 'Not specified'}",
        f"Supporting base : {st.session_state.supporting_base or 'Not specified'}",
        f"Idiomuscular reaction : {st.session_state.idiomuscular_reaction or 'Not specified'}",
        f"Rigor : {st.session_state.rigor or 'Not specified'}",
        f"Lividity : {st.session_state.lividity or 'Not specified'}",
        f"Lividity disappearance : {st.session_state.lividity_disappearance or 'Not specified'}",
        f"Lividity mobility : {st.session_state.lividity_mobility or 'Not specified'}"
        ]

    rect_width = 200
    line_height = 15
    margin = 10
    x_start = width - rect_width - margin

    # Calculate required height for text
    total_height = margin * 2
    for text in user_inputs:
        text_width = c.stringWidth(text, "Helvetica", 10)
        lines_needed = max(1, math.ceil(text_width / (rect_width - 2*margin)))
        total_height += line_height * lines_needed

    # Draw blue rectangle with calculated height
    rect_height = total_height
    c.setStrokeColorRGB(0, 0, 1)  # Blue color
    c.setFillColorRGB(0.9, 0.9, 1)  # Light blue fill color
    c.rect(x_start, height - 50 - rect_height, rect_width, rect_height, stroke=1, fill=1)

    # Reset text color to black
    c.setFillColorRGB(0, 0, 0)

    # Draw user inputs with word wrapping
    y_position = (height - 55 - rect_height) + rect_height - margin
    for text in user_inputs:
        words = text.split()
        line = []
        for word in words:
            line.append(word)
            test_line = ' '.join(line)
            text_width = c.stringWidth(test_line, "Helvetica", 10)
            
            if text_width > rect_width - 2*margin:
                # Draw the line without the last word
                line.pop()
                c.drawString(x_start + margin, y_position, ' '.join(line))
                line = [word]
                y_position -= line_height
                
        # Draw remaining words
        if line:
            c.drawString(x_start + margin, y_position, ' '.join(line))
            y_position -= line_height

    # Draw results starting right under title
    if hasattr(st.session_state, 'results') and st.session_state.results:
        y_position = height - 80  # Start under title
        text_lines = st.session_state.results.split('\n')
        
        for line in text_lines:
            if y_position < 50:
                c.showPage()
                y_position = height - 50

            if not line.strip():  # Skip empty lines but maintain spacing
                y_position -= 15
                continue

            if line.startswith('**') and line.endswith('**'):
                # Entirely bold line
                draw_formatted_text(line, 50, y_position, is_bold=True)
            elif '**' in line:
                # Line contains bold sections
                parts = line.split('**')
                x_position = 50
                for i, part in enumerate(parts):
                    if not part:  # Skip empty parts
                        continue
                    is_bold = (i % 2 == 1)  # Alternate between normal and bold
                    draw_formatted_text(part, x_position, y_position, is_bold=is_bold)
                    # Calculate next x position based on text width
                    font = "Helvetica-Bold" if is_bold else "Helvetica"
                    x_position += c.stringWidth(part, font, 12)
            else:
                # Normal text
                draw_formatted_text(line, 50, y_position, is_bold=False)
            
            y_position -= 15

    # Page 2: Graphs
    c.showPage()
    c.setPageSize(landscape(letter))
    width, height = landscape(letter)

    # Graph area
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 30, "Graph 1 : Henssge Evolution (Rectal)")
    c.drawString(width / 2 + 50, height - 30, "Graph 2 : Henssge Evolution (Brain)")
    c.drawString(50, height / 2 - 30, "Graph 3 : Methods Comparison")

    # Add graphs if they exist
    if hasattr(st.session_state, 'fig_henssge') and st.session_state.fig_henssge is not None:
        img_data_1 = io.BytesIO()
        st.session_state.fig_henssge.savefig(img_data_1, format='png')
        img_data_1.seek(0)
        img_1 = ImageReader(img_data_1)
        img_width_1, img_height_1 = img_1.getSize()
        scale_1 = min((width/2 - 30) / img_width_1, (height/2 - 30) / img_height_1)
        final_width_1 = img_width_1 * scale_1
        final_height_1 = img_height_1 * scale_1
        c.drawImage(img_1, 20, height - 50 - final_height_1, width=final_width_1, height=final_height_1)
        img_data_1.close()

    if hasattr(st.session_state, 'fig_henssge_brain') and st.session_state.fig_henssge_brain is not None:
        img_data_2 = io.BytesIO()
        st.session_state.fig_henssge_brain.savefig(img_data_2, format='png')
        img_data_2.seek(0)
        img_2 = ImageReader(img_data_2)
        img_width_2, img_height_2 = img_2.getSize()
        scale_2 = min((width/2 - 30) / img_width_2, (height/2 - 30) / img_height_2)
        final_width_2 = img_width_2 * scale_2
        final_height_2 = img_height_2 * scale_2
        c.drawImage(img_2, width/2 + 20, height - 50 - final_height_2, width=final_width_2, height=final_height_2)
        img_data_2.close()

    if hasattr(st.session_state, 'fig_comparison') and st.session_state.fig_comparison is not None:
        img_data_3 = io.BytesIO()
        st.session_state.fig_comparison.savefig(img_data_3, format='png')
        img_data_3.seek(0)
        img_3 = ImageReader(img_data_3)
        img_width_3, img_height_3 = img_3.getSize()
        scale_3 = min((width - 20) / img_width_3, (height/2 - 20) / img_height_3)
        final_width_3 = img_width_3 * scale_3
        final_height_3 = img_height_3 * scale_3
        c.drawImage(img_3, 00, 40, width=final_width_3, height=final_height_3)
        img_data_3.close()

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# User interface
st.title("EasyPMI")

# Picture path
image_path1 = "Images/Image_1.PNG"
image_path2 = "Images/Image_2.PNG"

# Help section
with st.expander("Help and User Guide", expanded=True):
    tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Cooling Methods", "Thanatological Signs", "Parameters"])
    
    with tab1:
        st.markdown("""
        ##### Introduction
        Welcome to EasyPMI, the Post-Mortem Interval Calculator.\n
        This application helps estimate the time since death using various methods and parameters.
        
        ##### Quick Tutorial
        1. **Navigation**: Use the sidebar on the left to enter parameters
        2. **Data Entry**: Use ↹ (*Tab*) to to validate a variable and automatically move to the next field.  
            a. You can manually determine the corrective factor, it will deactivate dropdnown lists.  
            b. You can use predefined corrective factor : 'Body Condition', 'Environment', 'Supporting base' dropdown lists.*
        3. **Calculate**: Click "Calculate" to get the results
        4. **Reset**: Click "Reset" to clear entries
        5. **Save**: Click "Download PDF" saves your results in PDF format
        
        ##### Error Handling
        If you encounter errors, check that input values are within acceptable ranges.
        The application will guide you with specific error messages.  
        In case of difficulties, you can contact us by sending the error message for correction of any potential bugs. 
        """)
        
    with tab2:
        st.markdown("""
        ##### Henssge Method
        - Use rectal or brain temperature
        - Non-linear cooling model
        - The cerebral temperature is replaced here by the tympanic temperature.
        - Body weight is required for rectal equation
        - Corrective factor is automatically adjusted based on weight
        
        ##### Baccino Method
        - Uses tympanic temperature
        - Linear cooling model
        - Simpler approach
        - Body weight is not required
        """)
        
    with tab3:
        st.markdown("""
        ##### Idiomuscular Reaction
        - Contraction after direct percussion of the muscle (*biceps brachii, for example*).
        - Zsako phenomenon -  Muscle contraction leading to flexion of the limb.
        - Strong and reversible - Visible contraction band that can be seen with the naked eye.
        - Weak and persistent - Discrete, localized contraction that is not visible but palpable.

        ##### Type of Rigor
        - Rigidity Not Established - There is no evidence of rigor mortis having set in.
        - Possible Re-establishment - Early signs of rigor mortis may be present, but it is not fully established.
        - Complete Rigidity - Rigor mortis is fully established, with the body exhibiting maximal stiffness.
        - Persistence - Rigor mortis persists or may be partially resolved.
        - Resolution - Rigor mortis has fully resolved.  
        *Be careful with Rigor: at extreme temperatures, the limits described in the literature are not applicable.
        High temperatures significantly accelerate the onset of rigor mortis, while low temperatures prolong it. "The corpses of strong persons can stay stiff till 8 - 10 and more days in air of 2.5 to 7.5°C" ; 1856, Kussmaul.*

        ##### Type of Lividity
        - Absent - There is no lividity present.
        - Development - Lividity is beginning to develop.
        - Confluence - Lividity is becoming more pronounced and merging.
        - Maximum - Lividity has reached its maximum intensity.

        ##### Lividity Mobility
        - Complete - Lividity can be completely displaced when the body is turned.
        - Partial - Lividity can be partially displaced when the body is turned.
        - Only little pallor - Lividity shows only a slight change in color (*or non change*) when the body is turned.

        ##### Disappearance of Lividity
        - Complete disappearance - Lividity disappears totaly at light pressure.
        - Incomplete disappearance - Lividity might disappears only with strong pressure (*with forceps*).
        """)

    with tab4:
        st.markdown("""
        ##### Temperature 
        - Methods based on body cooling are applicable if thermal conditions are 'stable'
        - Tympanic temperature can vary from one ear to the other *(especially if one is on the floor)*  
        *Not applicable in cases of major head trauma, or if wearing warm beanie*
        
        ##### Body Factors
        - **Weight**: The risk of error increases for extreme weights (low or high)
        - **Body Condition, Environment and Supporting base**: The corrective factor is based on the table established by Henssge
        - **Corrective Factor**: Manual adjustment for more precision  
        *The corrective factor is automatically adjusted based on body weight using the equation developed by Henssge*
        
        ##### Corrective Factor Table
        """)
        st.image(image_path1, caption="Empiric corrective factors of the body weight in context of thermally indifferent ground under body and applied to a body weight of 70 kg. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")
        st.image(image_path2, caption="Adaptation of corrective factors to ground under body. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")

# Initialize session variables
if 'input_t_tympanic' not in st.session_state:
    st.session_state.input_t_tympanic = ""
if 'input_t_rectal' not in st.session_state:
    st.session_state.input_t_rectal = ""
if 'input_t_ambient' not in st.session_state:
    st.session_state.input_t_ambient = ""
if 'input_M' not in st.session_state:
    st.session_state.input_M = ""
if 'input_Cf' not in st.session_state:
    st.session_state.input_Cf = ""
if 'body_condition' not in st.session_state:
    st.session_state.body_condition = "Not specified"
if 'environment' not in st.session_state:
    st.session_state.environment = "Not specified"
if 'supporting_base' not in st.session_state:
    st.session_state.supporting_base = "Not specified"    
if 'idiomuscular_reaction' not in st.session_state:
    st.session_state.idiomuscular_reaction = "Not specified"
if 'rigor' not in st.session_state:
    st.session_state.rigor = "Not specified"
if 'lividity' not in st.session_state:
    st.session_state.lividity = "Not specified"
if 'lividity_disappearance' not in st.session_state:
    st.session_state.lividity_disappearance = "Not specified"
if 'lividity_mobility' not in st.session_state:
    st.session_state.lividity_mobility = "Not specified"
if 'results' not in st.session_state:
    st.session_state.results = ""
if 'fig_henssge' not in st.session_state:
    st.session_state.fig_henssge = None
if 'fig_henssge_brain' not in st.session_state:
    st.session_state.fig_henssge_brain = None
if 'fig_comparison' not in st.session_state:
    st.session_state.fig_comparison = None

# User inputs
st.sidebar.header("Parameters")

# Text inputs with session_state keys
st.sidebar.text_input(
    "Tympanic temperature (°C) : ",
    key="input_t_tympanic"
)

st.sidebar.text_input(
    "Rectal temperature (°C) : ",
    key="input_t_rectal"
)

st.sidebar.text_input(
    "Ambient temperature (°C) : ",
    key="input_t_ambient"
)

st.sidebar.text_input(
    "Body weight (kg) : ",
    key="input_M"
)

st.sidebar.text_input(
    "Corrective factor (Cf) : ",
    key="input_Cf"
)

# Condition to disable dropdowns
body_condition_disabled = bool(st.session_state.input_Cf)
environment_disabled = bool(st.session_state.input_Cf)
supporting_base_disabled = bool(st.session_state.input_Cf)

# Selectbox with session_state keys
st.sidebar.selectbox(
    "Body condition :",
    ['Not specified', 'naked', 'lightly dressed (one to two thin layers)', 
     'moderately dressed (two to three thin layers)', 
     'warmly dressed (thick layers)', 'very dressed (thick blanket)'],
    key="body_condition",
    disabled=body_condition_disabled
)

st.sidebar.selectbox(
    "Environment :",
    ['Not specified', 'still air', 'moving air', 'wet and still air',
     'wet and moving air', 'still water', 'flowing water'],
    key="environment",
    disabled=environment_disabled
)

st.sidebar.selectbox(
    "Supporting base :",
    ['Not specified', 'Indifferent', 'Heavy padding', 'Mattress (bed), thick carpet',
     'About 2 cm wettish leaves', 'About 2 cm totally dry leaves', 'Concrete, stony, tiled'],
    key="supporting_base",
    disabled=supporting_base_disabled
)

# Thanatological signs
st.sidebar.header("Thanatological Signs")
st.sidebar.selectbox(
    "Idiomuscular Reaction :",
    ['Not specified', 'zsako', 'strong reversible', 'weak persistent', 'no reaction'],
    key="idiomuscular_reaction"
)

st.sidebar.selectbox(
    "Type of Rigor :",
    ['Not specified', 'Rigidity not established', 'Possible re-establishment',
     'Complete rigidity', 'Persistence', 'Resolution'],
    key="rigor"
)

st.sidebar.selectbox(
    "Type of Lividity :",
    ['Not specified', 'Absent', 'Development', 'Confluence', 'Maximum'],
    key="lividity"
)

st.sidebar.selectbox(
    "Lividity Mobility :",
    ['Not specified', 'Complete', 'Partial', 'Only little pallor'],
    key="lividity_mobility"
)

st.sidebar.selectbox(
    "Disappearance of Lividity :",
    ['Not specified', 'Incomplete disappearence', 'Complete disappearance'],
    key="lividity_disappearance"
)

# Action buttons
if st.sidebar.button("Calculate"):
    calculate_results()

if st.sidebar.button("Reset"):
    reset()

pdf_download = st.sidebar.download_button(
    label="Download PDF",
    data=generate_pdf() if 'clicked' not in st.session_state else None,
    file_name="results.pdf",
    mime="application/pdf",
    key='pdf_button'
)

if pdf_download:
    st.success("PDF downloaded successfully")
    
# Display results
st.header("Results")
st.write(st.session_state.results)

# Display graphs
if st.session_state.fig_henssge:
    st.pyplot(st.session_state.fig_henssge)
if st.session_state.fig_henssge_brain:
    st.pyplot(st.session_state.fig_henssge_brain)
if st.session_state.fig_comparison:
    st.pyplot(st.session_state.fig_comparison)


