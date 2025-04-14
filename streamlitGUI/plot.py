import math
from typing import Optional
from datetime import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from core.computations import henssge_rectal, henssge_brain
from core.constants import STANDARD_BODY_TEMPERATURE
from core.input_parameters import InputParameters
from core.output_results import HenssgeRectalResults, HenssgeBrainResults, OutputResults, PostMortemIntervalResults
from core.tools import format_time as format_relative_time
from core.datetime_utils import format_datetime, subtract_hours_from_datetime


def plot_temperature_henssge_rectal(input_parameters: InputParameters, result: HenssgeRectalResults) -> Optional[Figure]:
    """
    Plots the post-mortem thermal decay curve according to the Henssge equation.

    This function generates a Matplotlib plot representing the evolution of the
    rectal temperature over time, based on the Henssge model for rectal temperature.
    The plot includes the theoretical curve, the current measurement point, and the
    confidence interval.

    Parameters
    ----------
    input_parameters : InputParameters
        input_parameters from user
    result : HenssgeRectalResults
        result from Henssge rectal computation

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """
    
    # Check result
    if result.error_message or result.post_mortem_interval is None:
        return None
    measurement_dt = input_parameters.measurement_datetime
    
    # Prepare figure
    fig = Figure(figsize=(6, 4), dpi=150)
    ax = fig.add_subplot(111)

    # Build temperatures through time
    max_time = max(50, result.pmi_max() * 1.2 if result.pmi_max() else 50)
    time = np.linspace(0, max_time, 100)
    temperatures = [input_parameters.ambient_temperature 
                    + (STANDARD_BODY_TEMPERATURE - input_parameters.ambient_temperature) 
                    * henssge_rectal.temperature_decrease(t, input_parameters.ambient_temperature, input_parameters.body_mass * result.corrective_factor) for
                    t in time]

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=input_parameters.rectal_temperature, color='r', linestyle='--', label=f"Current temperature: {input_parameters.rectal_temperature} °C")
    
    # --- Format labels based on measurement_dt ---
    pmi_estimate_hrs = result.post_mortem_interval
    pmi_min_hrs = result.pmi_min()
    pmi_max_hrs = result.pmi_max()

    if measurement_dt:
        time_of_death_estimate = subtract_hours_from_datetime(measurement_dt, pmi_estimate_hrs)
        time_of_death_start = subtract_hours_from_datetime(measurement_dt, pmi_min_hrs) # Later time of death
        time_of_death_end = subtract_hours_from_datetime(measurement_dt, pmi_max_hrs)   # Earlier time of death

        est_label = f"Est. Death: {format_datetime(time_of_death_estimate)}"
        ci_label = f"CI: {format_datetime(time_of_death_end)} - {format_datetime(time_of_death_start)}"
        ax.scatter(pmi_estimate_hrs, input_parameters.rectal_temperature, color='b', label=est_label)
        ax.axvspan(pmi_min_hrs, pmi_max_hrs, color='green', alpha=0.3, label=ci_label)
    else:
        est_label = f"Est. Time: {format_relative_time(pmi_estimate_hrs)}"
        ci_label = f"CI: {format_relative_time(pmi_min_hrs)} - {format_relative_time(pmi_max_hrs)}"
        ax.scatter(pmi_estimate_hrs, input_parameters.rectal_temperature, color='b', label=est_label)
        ax.axvspan(pmi_min_hrs, pmi_max_hrs, color='green', alpha=0.3, label=ci_label)
    # --- End Formatting ---

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Rectal temperature (°C)")
    ax.set_title("Evolution of rectal temperature", fontsize=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1), prop={'size': 8}, fancybox=True, shadow=True)
    ax.grid(True)

    return fig


def plot_temperature_henssge_brain(input_parameters: InputParameters, result: HenssgeBrainResults) -> Optional[Figure]:
    """
    Plots the post-mortem brain thermal decay curve according to the Henssge equation.

    This function generates a Matplotlib plot representing the evolution of the
    tympanic temperature (an indicator of brain temperature) over time. The model
    uses a specific Henssge equation for brain cooling, which differs from the one
    used for rectal temperature in its constants and simplified form (no dependence
    on body mass).

    Parameters
    ----------
    input_parameters : InputParameters
        input_parameters from user
    result : HenssgeBrainResults
        result from Henssge brain computation

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """

    # Check result
    if result.error_message or result.post_mortem_interval is None:
        return None
    measurement_dt = input_parameters.measurement_datetime

    # Prepare figure
    fig = Figure(figsize=(6, 4), dpi=150)
    ax = fig.add_subplot(111)

    # Build temperatures through time
    max_time = max(50, result.pmi_max() * 1.2 if result.pmi_max() else 50)
    time = np.linspace(0, max_time, 100)
    temperatures = [input_parameters.ambient_temperature
                    + (STANDARD_BODY_TEMPERATURE - input_parameters.ambient_temperature)
                    * henssge_brain.temperature_decrease(t) 
                    for t in time]

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=input_parameters.tympanic_temperature, color='r', linestyle='--', label=f"Current temperature : {input_parameters.tympanic_temperature} °C")
    
    # --- Format labels based on measurement_dt ---
    pmi_estimate_hrs = result.post_mortem_interval
    pmi_min_hrs = result.pmi_min()
    pmi_max_hrs = result.pmi_max()

    if measurement_dt:
        time_of_death_estimate = subtract_hours_from_datetime(measurement_dt, pmi_estimate_hrs)
        time_of_death_start = subtract_hours_from_datetime(measurement_dt, pmi_min_hrs) # Later time of death
        time_of_death_end = subtract_hours_from_datetime(measurement_dt, pmi_max_hrs)   # Earlier time of death

        est_label = f"Est. Death: {format_datetime(time_of_death_estimate)}"
        ci_label = f"CI: {format_datetime(time_of_death_end)} - {format_datetime(time_of_death_start)}"
        ax.scatter(pmi_estimate_hrs, input_parameters.tympanic_temperature, color='b', label=est_label)
        ax.axvspan(pmi_min_hrs, pmi_max_hrs, color='green', alpha=0.3, label=ci_label)
    else:
        est_label = f"Est. Time: {format_relative_time(pmi_estimate_hrs)}"
        ci_label = f"CI: {format_relative_time(pmi_min_hrs)} - {format_relative_time(pmi_max_hrs)}"
        ax.scatter(pmi_estimate_hrs, input_parameters.tympanic_temperature, color='b', label=est_label)
        ax.axvspan(pmi_min_hrs, pmi_max_hrs, color='green', alpha=0.3, label=ci_label)
    # --- End Formatting ---

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Tympanic temperature (°C)")
    ax.set_title("Evolution of tympanic temperature", fontsize=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1), prop={'size': 8}, fancybox=True, shadow=True)
    ax.grid(True)

    return fig

# --- Comparative Plot Utilities ---

def _hybrid_scale(x, threshold=20, compression_factor=8):
    """Custom hybrid scale transformation for the X-axis."""
    return np.where(x <= threshold, x, threshold + (x - threshold) / compression_factor)

def _inverse_hybrid_scale(x, threshold=20, compression_factor=8):
    """Inverse of the hybrid scale transformation."""
    return np.where(x <= threshold, x, threshold + (x - threshold) * compression_factor)

def _add_mustache_box(ax: plt.Axes, vertical_index: int, left_hrs: float, right_hrs: float, color: str, center_hrs: Optional[float] = None, measurement_dt: Optional[datetime] = None) -> None:
    """
    Draws a mustache box, formatting labels with absolute time if measurement_dt is provided.
    """
    vertical_offset = 0.4 
    plot_center_hrs = center_hrs if center_hrs is not None else (left_hrs + right_hrs) / 2.0
    
    # Calculate absolute times if possible
    center_dt = subtract_hours_from_datetime(measurement_dt, center_hrs) if measurement_dt and center_hrs is not None else None
    start_dt = subtract_hours_from_datetime(measurement_dt, left_hrs) if measurement_dt else None # Later ToD
    end_dt = subtract_hours_from_datetime(measurement_dt, right_hrs) if measurement_dt else None  # Earlier ToD

    # Format labels
    center_label = format_datetime(center_dt) if center_dt else format_relative_time(center_hrs) if center_hrs is not None else ""
    left_label = format_datetime(start_dt) if start_dt else format_relative_time(left_hrs)
    right_label = format_datetime(end_dt) if end_dt else format_relative_time(right_hrs)

    # Text Positioning
    if center_hrs is not None: # Text ABOVE
        ax.text(center_hrs, vertical_index + vertical_offset, center_label, ha='center', va='bottom', fontsize=9, color=color, rotation=0) # Smaller font
    # Text BELOW
    ax.text(left_hrs, vertical_index - vertical_offset, left_label, ha='center', va='top', fontsize=9, color=color, rotation=0) # Smaller font
    ax.text(right_hrs, vertical_index - vertical_offset, right_label, ha='center', va='top', fontsize=9, color=color, rotation=0) # Smaller font

    # Error Bar (remains plotted in hours)
    ax.errorbar([plot_center_hrs], [vertical_index], xerr=[[plot_center_hrs - left_hrs], [right_hrs - plot_center_hrs]],
                fmt='o', markersize=4, color=color, capsize=4, lw=1.5)

def _add_zone_box(ax: plt.Axes, vertical_index: int, position_hrs: float, valid_side: str, color: str, measurement_dt: Optional[datetime] = None) -> None:
    """Draws a shaded zone, formatting labels with absolute time if measurement_dt is provided."""
    x_min_lim, x_max_lim = ax.get_xlim()
    left_shade_hrs, right_shade_hrs = x_min_lim, x_max_lim
    text, text_horizontal_align = "", ""

    position_dt = subtract_hours_from_datetime(measurement_dt, position_hrs) if measurement_dt else None
    pos_label = format_datetime(position_dt) if position_dt else format_relative_time(position_hrs)

    if valid_side == 'upper': 
        text = f"PMI > {pos_label}"
        text_horizontal_align = 'left'
        right_shade_hrs = position_hrs
    elif valid_side == 'lower': 
        text = f"PMI < {pos_label}"
        text_horizontal_align = 'right'
        left_shade_hrs = position_hrs
    else:
        return

    ax.axvspan(xmin=left_shade_hrs, xmax=right_shade_hrs, color="grey", alpha=0.15, zorder=-1)
    ax.axvline(x=position_hrs, color=color, linestyle='--', lw=1.5)
    ax.text(position_hrs, vertical_index, text, ha=text_horizontal_align, va='center', fontsize=9, color=color, # Smaller font
        bbox=dict(facecolor='white', alpha=0.7, pad=0.1, boxstyle='round,pad=0.2'))

def _plot_post_mortem_interval_result(ax: plt.Axes, vertical_index: int, result: PostMortemIntervalResults, color: str, measurement_dt: Optional[datetime] = None) -> None:
    """ Determines plot type (mustache/zone) for signs and passes measurement_dt along. """
    if result is None or result.min is None or result.max is None or math.isnan(result.min) or math.isnan(result.max): return

    min_hrs = result.min
    max_hrs = result.max

    # Check for NaN/inf before comparison
    is_min_zero = not math.isnan(min_hrs) and np.isclose(min_hrs, 0.0)
    is_max_inf = not math.isnan(max_hrs) and max_hrs == float('inf')
    is_min_valid_nonzero = not math.isnan(min_hrs) and not np.isclose(min_hrs, 0.0)
    is_max_valid_finite = not math.isnan(max_hrs) and max_hrs != float('inf')


    if is_min_zero and is_max_valid_finite:
        _add_zone_box(ax, vertical_index, position_hrs=max_hrs, valid_side='lower', color=color, measurement_dt=measurement_dt)
    elif is_max_inf and is_min_valid_nonzero:
         _add_zone_box(ax, vertical_index, position_hrs=min_hrs, valid_side='upper', color=color, measurement_dt=measurement_dt)
    elif is_min_valid_nonzero and is_max_valid_finite:
         _add_mustache_box(ax, vertical_index, left_hrs=min_hrs, right_hrs=max_hrs, color=color, center_hrs=None, measurement_dt=measurement_dt)


# --- Main Comparative Plot Function ---

def plot_comparative_pmi_results(input_parameters: InputParameters, result: OutputResults) -> Optional[Figure]:
    """
    Plots a comparative graph with FIXED Y-axis, fixed size, and fixed colors.

    Generates a visualization comparing PMI estimates. Always displays all potential
    methods on the Y-axis in a fixed order. Figure size is fixed at (18, 5) for 
    PDF compatibility. Uses robust checks and axis limit calculations.

    Args:
        result: The main OutputResults object containing results from all computations.

    Returns:
        A Matplotlib Figure object with the comparative plot. May be empty visually
        if no methods were calculated, but axis labels will be present.
    """
    measurement_dt = input_parameters.measurement_datetime

    # --- Define Fixed Order and Colors for ALL Methods ---
    # Order determines top-to-bottom display after y-axis inversion
    ALL_METHODS_ORDERED = [
        'Henssge (Rectal)',
        'Henssge (Brain)',
        'Baccino (Global)',
        'Baccino (Interval)',
        'Idiomuscular Reaction',
        'Rigor Mortis',
        'Livor Mortis (Onset)',
        'Livor Mortis (Mobility)',
        'Livor Mortis (Disappearance)',
    ]
    num_total_methods = len(ALL_METHODS_ORDERED)

    # Fixed colors for each method
    method_color_map = {
        'Henssge (Rectal)': mcolors.TABLEAU_COLORS['tab:blue'], 
        'Henssge (Brain)': mcolors.TABLEAU_COLORS['tab:orange'],
        'Baccino (Global)': mcolors.TABLEAU_COLORS['tab:green'], 
        'Baccino (Interval)': mcolors.TABLEAU_COLORS['tab:red'],
        'Idiomuscular Reaction': mcolors.TABLEAU_COLORS['tab:purple'], 
        'Rigor Mortis': mcolors.TABLEAU_COLORS['tab:brown'],
        'Livor Mortis (Onset)': mcolors.TABLEAU_COLORS['tab:pink'], 
        'Livor Mortis (Mobility)': mcolors.TABLEAU_COLORS['tab:gray'],
        'Livor Mortis (Disappearance)': mcolors.TABLEAU_COLORS['tab:olive'],
        'default': mcolors.TABLEAU_COLORS['tab:cyan'] 
    }

    # --- Figure Setup with FIXED Size ---
    fig = Figure(figsize=(16, 6), dpi=200) 
    ax = fig.add_subplot(111)

    # --- Determine X-axis Limits ---
    relevant_x_values = []
    # Iterate through result attributes directly to find max X extent needed
    try: # Wrap checks in try-except for safety
        if result.henssge_rectal and not result.henssge_rectal.error_message:
            pmi_max = result.henssge_rectal.pmi_max()
            if pmi_max is not None and not math.isinf(pmi_max): relevant_x_values.append(pmi_max)
        if result.henssge_brain and not result.henssge_brain.error_message:
            pmi_max = result.henssge_brain.pmi_max()
            if pmi_max is not None and not math.isinf(pmi_max): relevant_x_values.append(pmi_max)
        if result.baccino and not result.baccino.error_message:
            if result.baccino.post_mortem_interval_global is not None and result.baccino.confidence_interval_global is not None:
                upper_bound = result.baccino.post_mortem_interval_global + result.baccino.confidence_interval_global
                if not math.isinf(upper_bound): relevant_x_values.append(upper_bound)
            if result.baccino.post_mortem_interval_interval is not None and result.baccino.confidence_interval_interval is not None:
                 upper_bound = result.baccino.post_mortem_interval_interval + result.baccino.confidence_interval_interval
                 if not math.isinf(upper_bound): relevant_x_values.append(upper_bound)
        for sign_res in [result.idiomuscular_reaction, result.rigor, result.lividity, result.lividity_disappearance, result.lividity_mobility]:
             if sign_res and sign_res.min is not None and sign_res.max is not None:
                if sign_res.max != float('inf'): relevant_x_values.append(sign_res.max)
                elif not np.isclose(sign_res.min, 0.0): relevant_x_values.append(sign_res.min)
    except AttributeError as e:
        print(f"Warning: Issue calculating X limits, some results might be missing: {e}")
        # Continue even if some attributes are missing

    # Determine overall max value for setting axis limits
    default_max_limit = 24 
    finite_values = [v for v in relevant_x_values if v is not None and not math.isnan(v) and not math.isinf(v)]
    actual_max_value = max(max(finite_values), default_max_limit) if finite_values else default_max_limit
    axis_limit_right = actual_max_value * 1.1 
    ax.set_xlim(left=-1.0, right=axis_limit_right) 
    ax.set_xscale('function', functions=(_hybrid_scale, _inverse_hybrid_scale))

    # --- Calculate Ticks for X-axis ---
    threshold = 20 
    ticks = list(range(0, threshold + 1, 4)) 
    if axis_limit_right > threshold:
        potential_ticks = [30, 40, 50, 60, 80, 100, 120, 150, 200, 250, 300]
        ticks.extend([t for t in potential_ticks if threshold < t <= axis_limit_right])
        if ticks and axis_limit_right > ticks[-1] * 1.1:
             last_tick_candidate = math.ceil(axis_limit_right / 10) * 10 
             if last_tick_candidate > ticks[-1] and last_tick_candidate <= axis_limit_right: ticks.append(last_tick_candidate)
    ax.set_xticks(ticks)

    # --- Plotting Loop (Iterating through ALL fixed methods) ---
    for y_index, label in enumerate(ALL_METHODS_ORDERED):
        item_color = method_color_map.get(label, method_color_map['default'])
        res_obj = None
        item_type = None
        is_valid_for_plotting = False

        # --- Find corresponding result and check validity ---
        try: 
            if label == 'Henssge (Rectal)' and result.henssge_rectal and not result.henssge_rectal.error_message and result.henssge_rectal.post_mortem_interval is not None:
                res_obj, item_type, is_valid_for_plotting = result.henssge_rectal, 'henssge_rectal', True
            elif label == 'Henssge (Brain)' and result.henssge_brain and not result.henssge_brain.error_message and result.henssge_brain.post_mortem_interval is not None:
                res_obj, item_type, is_valid_for_plotting = result.henssge_brain, 'henssge_brain', True
            elif label == 'Baccino (Global)' and result.baccino and not result.baccino.error_message and result.baccino.post_mortem_interval_global is not None and result.baccino.confidence_interval_global is not None:
                res_obj, item_type, is_valid_for_plotting = result.baccino, 'baccino_global', True
            elif label == 'Baccino (Interval)' and result.baccino and not result.baccino.error_message and result.baccino.post_mortem_interval_interval is not None and result.baccino.confidence_interval_interval is not None:
                res_obj, item_type, is_valid_for_plotting = result.baccino, 'baccino_interval', True
            elif label == 'Idiomuscular Reaction' and result.idiomuscular_reaction and result.idiomuscular_reaction.min is not None and result.idiomuscular_reaction.max is not None:
                 res_obj, item_type, is_valid_for_plotting = result.idiomuscular_reaction, 'sign', True
            elif label == 'Rigor Mortis' and result.rigor and result.rigor.min is not None and result.rigor.max is not None:
                 res_obj, item_type, is_valid_for_plotting = result.rigor, 'sign', True
            elif label == 'Livor Mortis (Onset)' and result.lividity and result.lividity.min is not None and result.lividity.max is not None:
                 res_obj, item_type, is_valid_for_plotting = result.lividity, 'sign', True
            elif label == 'Livor Mortis (Mobility)' and result.lividity_mobility and result.lividity_mobility.min is not None and result.lividity_mobility.max is not None:
                 res_obj, item_type, is_valid_for_plotting = result.lividity_mobility, 'sign', True
            elif label == 'Livor Mortis (Disappearance)' and result.lividity_disappearance and result.lividity_disappearance.min is not None and result.lividity_disappearance.max is not None:
                 res_obj, item_type, is_valid_for_plotting = result.lividity_disappearance, 'sign', True

            # --- If valid, plot it at the fixed y_index ---
            if is_valid_for_plotting:
                center_hrs, plot_min_hrs, plot_max_hrs = None, None, None
                # Determine hours for plotting
                if item_type in ['henssge_rectal', 'henssge_brain']:
                    center_hrs = res_obj.post_mortem_interval
                    plot_min_hrs, plot_max_hrs = res_obj.pmi_min(), res_obj.pmi_max()
                elif item_type == 'baccino_global':
                    center_hrs = res_obj.post_mortem_interval_global
                    if res_obj.confidence_interval_global is not None:
                        plot_min_hrs = center_hrs - res_obj.confidence_interval_global
                        plot_max_hrs = center_hrs + res_obj.confidence_interval_global
                elif item_type == 'baccino_interval':
                    center_hrs = res_obj.post_mortem_interval_interval
                    if res_obj.confidence_interval_interval is not None:
                         plot_min_hrs = center_hrs - res_obj.confidence_interval_interval
                         plot_max_hrs = center_hrs + res_obj.confidence_interval_interval
                elif item_type == 'sign':
                    # Signs are handled by _plot_post_mortem_interval_result
                    pass
                # Plot using appropriate function, passing measurement_dt
                if item_type == 'sign':
                    _plot_post_mortem_interval_result(ax, y_index, res_obj, color=item_color, measurement_dt=measurement_dt)
                elif plot_min_hrs is not None and plot_max_hrs is not None:
                    _add_mustache_box(ax, y_index, left_hrs=plot_min_hrs, right_hrs=plot_max_hrs, color=item_color, center_hrs=center_hrs, measurement_dt=measurement_dt)
        except Exception as e: # Catch any unexpected error during processing/plotting
             print(f"Error processing or plotting item '{label}': {e}")
             ax.text(ax.get_xlim()[0] + 1, y_index, "Error", color='red', fontsize=8)
        # If not is_valid_for_plotting, the loop continues, leaving the row blank

    # --- Final Touches ---
    # Set fixed Y ticks and labels
    ax.set_yticks(range(num_total_methods))
    ax.set_yticklabels(ALL_METHODS_ORDERED)
    
    # Set fixed Y limits with margins (important for consistent look)
    ax.set_ylim(bottom=-0.5, top=num_total_methods - 0.5) 

    # Color Y-axis tick labels using the fixed map
    for ytick in ax.get_yticklabels(): 
        label_text = ytick.get_text()
        tick_color = method_color_map.get(label_text, method_color_map['default']) 
        ytick.set_color(tick_color) 
        ytick.set_fontsize(11) 

    ax.set_ylabel('Method', labelpad=10, fontsize=14) 
    ax.set_xlabel('Estimated Post-Mortem Interval (hours)', fontsize=14)
    ax.set_title('Comparison of Estimated Post-Mortem Intervals', pad=10, fontsize=16)

    # Add grid only on X axis
    ax.grid(True, alpha=0.4, axis='x', linestyle=':') 

    ax.tick_params(axis='x', labelsize=10) 
    
    # Invert y-axis so the first item in ALL_METHODS_ORDERED is at the top
    ax.invert_yaxis()
    
    # Restore Manual Margin Adjustment for Fixed Size
    fig.subplots_adjust(left=0.22, bottom=0.15, top=0.9, right=0.95) 

    return fig