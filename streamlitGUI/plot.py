import math
from typing import Optional

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from core.computations import henssge_rectal, henssge_brain
from core.constants import STANDARD_BODY_TEMPERATURE
from core.input_parameters import InputParameters
from core.output_results import HenssgeRectalResults, HenssgeBrainResults, OutputResults, PostMortemIntervalResults
from core.tools import format_time


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
    if result.error_message:
        return None
    
    # Prepare figure
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Build temperatures through time
    max_time = 50
    time = np.linspace(0, max_time, 100)
    temperatures = [input_parameters.ambient_temperature 
                    + (STANDARD_BODY_TEMPERATURE - input_parameters.ambient_temperature) 
                    * henssge_rectal.temperature_decrease(t, input_parameters.ambient_temperature, input_parameters.body_mass * result.corrective_factor) for
                    t in time]

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=input_parameters.rectal_temperature, color='r', linestyle='--', label=f"Current temperature: {input_parameters.rectal_temperature} °C")
    ax.scatter(result.post_mortem_interval, input_parameters.rectal_temperature, color='b', label=f"Estimated time: {format_time(result.post_mortem_interval)}")

    ax.axvspan(result.pmi_min(), result.pmi_max(), color='green', alpha=0.3, label=f"CI: {format_time(result.pmi_min())} - {format_time(result.pmi_max())}")

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
    if result.error_message:
        return None

    # Prepare figure
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Build temperatures through time
    max_time = 50
    time = np.linspace(0, max_time, 100)
    temperatures = [input_parameters.ambient_temperature
                    + (STANDARD_BODY_TEMPERATURE - input_parameters.ambient_temperature)
                    * henssge_brain.temperature_decrease(t) 
                    for t in time]

    ax.plot(time, temperatures, label="Thermal evolution")
    ax.axhline(y=input_parameters.tympanic_temperature, color='r', linestyle='--', label=f"Current temperature : {input_parameters.tympanic_temperature} °C")
    ax.scatter(result.post_mortem_interval, input_parameters.tympanic_temperature, color='b', label=f"Estimated time : {format_time(result.post_mortem_interval)}")

    ax.axvspan(result.pmi_min(), result.pmi_max(), color='green', alpha=0.3, label=f"CI : {format_time(result.pmi_min())} - {format_time(result.pmi_max())}")

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Tympanic temperature (°C)")
    ax.set_title("Evolution of tympanic temperature", fontsize=12)

    ax.legend(loc='upper right', bbox_to_anchor=(1, 1), prop={'size': 8}, fancybox=True, shadow=True)
    ax.grid(True)

    return fig

# Plot Tools
def _hybrid_scale(x, threshold=20, compression_factor=8):
    """
    Custom hybrid scale transformation.
    Values below the threshold are linear, values above are compressed.
    """
    return np.where(x <= threshold, x, threshold + (x - threshold) / compression_factor)


def _inverse_hybrid_scale(x, threshold=20, compression_factor=8):
    """
    Inverse of the hybrid scale transformation.
    """
    return np.where(x <= threshold, x, threshold + (x - threshold) * compression_factor)

def _pick_color(index: int) -> str:
    return list(mcolors.TABLEAU_COLORS.values())[index]
    

# Mustaches boxes
def _add_vertical_bars(ax: plt.Axes, x1: float, x2: float, y: float, color: str) -> float:
    bar_height = 0.05
    ax.plot([x1, x1], [y - bar_height, y + bar_height], color=color, lw=2)
    ax.plot([x2, x2], [y - bar_height, y + bar_height], color=color, lw=2)
    return bar_height


def _add_interval_values(ax: plt.Axes, x1: float, x2: float, y: float, bar_height: float, color: str) -> None:
    ax.text(x1, y - bar_height - 0.03, f"{format_time(x1)}", ha='center', va='top', fontsize=10, color=color)
    ax.text(x2, y - bar_height - 0.03, f"{format_time(x2)}", ha='center', va='top', fontsize=10, color=color)


def _add_mustache_box(ax: plt.Axes, vertical_index: int, left: float, right: float, center: float = None) -> None:
    color = _pick_color(vertical_index)
    if center:
        ax.text(center, vertical_index, f"{format_time(center)}", ha='center', va='bottom', fontsize=8)
    else:
        center = (right + left) / 2.0

    ax.errorbar([center], [vertical_index], xerr=[[center - left], [right - center]], fmt='o', color=color)
    bar_height = _add_vertical_bars(ax, left, right, vertical_index, color)
    _add_interval_values(ax, left, right, vertical_index, bar_height, color)


# Zone boxes
def _add_zone_box(ax: plt.Axes, vertical_index: int, position: float, valid_side: str) -> None:
    color = _pick_color(vertical_index)
    x_min, x_max = ax.get_xlim()
    
    left = 0.0
    right = 0.0
    text = ""
    direction = ""
    if valid_side == 'upper':
        text = f"PMI > {format_time(position)}"
        direction = 'right'
        left = position
        right = x_max
    elif valid_side == 'lower':
        text = f"PMI < {format_time(position)}"
        direction = 'left'
        left = x_min
        right = position

    ax.axvspan(xmin=left, xmax=right, color=color, alpha=0.2)
    ax.axvline(x=position, color=color, linestyle='--', lw=2)
    ax.text(position, vertical_index, text, ha=direction, va='bottom', fontsize=8, color=color)


# PostMortemInterval plots
def _plot_post_mortem_interval_result(ax: plt.Axes, vertical_index: int, result: PostMortemIntervalResults) -> None:
    if result.min == 0.0:
        _add_zone_box(ax, vertical_index, position=result.max, valid_side='lower')
    elif result.max == float('inf'):
        _add_zone_box(ax, vertical_index, position=result.min, valid_side='upper')
    if result.min != 0.0 and result.max != float('inf'):
        _add_mustache_box(ax, vertical_index, left=result.min, right=result.max)


def plot_comparative_pmi_results(result: OutputResults) -> Optional[Figure]:
    """
    Plots a comparative graph of different post-mortem interval (PMI) estimations.

    This function generates a comparative visualization of different PMI estimation methods,
    including the Henssge method, the Baccino method, and thanatological signs (rigor, lividity, etc.).

    Parameters
    ----------
    result : OutputResults
        result from computation

    Returns
    -------
    Figure
        Matplotlib Figure with the plotted graph.
    """
    fig = Figure(figsize=(18, 5), dpi=120)
    ax = fig.add_subplot(111)

    # --- Gradutions
    # Create Custom Graduations
    ticks = list(range(0, 21, 4))
    values = [v for v in [result.henssge_rectal.pmi_max(), result.henssge_brain.pmi_max(), result.baccino.post_mortem_interval_interval,
                          result.baccino.post_mortem_interval_global, result.idiomuscular_reaction.max, result.rigor.max, result.lividity.max,
                          result.lividity_disappearance.max, result.lividity_mobility.max] if v is not None]
    if result.baccino.confidence_interval_interval is not None:
        values.append(result.baccino.post_mortem_interval_interval + result.baccino.confidence_interval_interval)
    if result.baccino.confidence_interval_global is not None:
        values.append(result.baccino.post_mortem_interval_global + result.baccino.confidence_interval_global)
    max_value = max(values) if values else 0

    if max_value <= 20:
        ticks = list(range(0, int(max_value) + 1, 4))
    else:
        log_ticks = [30, 40, 50, 60, 80, 100]  # create logarithmic graduations after 20h
        ticks.extend([t for t in log_ticks if t <= max_value])

    # Determine max value for the x-axis
    default_max = 10  # defaut value for the x-axis
    filtered_max_values = [v for v in values if not (math.isinf(v) or math.isnan(v))]
    max_value = max(max(filtered_max_values) if filtered_max_values else default_max, default_max)

    ax.set_xlim(left=0.0, right=max_value)

    # Apply a custom transformation to the x-axis
    ax.set_xscale('function', functions=(_hybrid_scale, _inverse_hybrid_scale))

    # --- Plots
    vertical_index = 0
    vertical_labels = []    
    
    # Henssge rectal
    if result.henssge_rectal.post_mortem_interval is not None and result.henssge_rectal.confidence_interval is not None:
        _add_mustache_box(ax, vertical_index, center=result.henssge_rectal.post_mortem_interval, left=result.henssge_rectal.pmi_min(), right=result.henssge_rectal.pmi_max())
        vertical_labels.append('Henssge (Rectal)')
        vertical_index += 1

    # Henssge brain
    if result.henssge_brain.post_mortem_interval is not None and result.henssge_brain.confidence_interval is not None:
        _add_mustache_box(ax, vertical_index, center=result.henssge_brain.post_mortem_interval, left=result.henssge_brain.pmi_min(), right=result.henssge_brain.pmi_max())
        vertical_labels.append('Henssge (Brain)')
        vertical_index += 1

    # Baccino interval
    if result.baccino.post_mortem_interval_interval is not None and result.baccino.confidence_interval_interval is not None:
        _add_mustache_box(ax, vertical_index,
                          center=result.baccino.post_mortem_interval_interval,
                          left=result.baccino.post_mortem_interval_interval - result.baccino.confidence_interval_interval,
                          right=result.baccino.post_mortem_interval_interval + result.baccino.confidence_interval_interval)
        vertical_labels.append('Baccino\n(Interval)')
        vertical_index += 1

    # Baccino global
    if result.baccino.post_mortem_interval_global is not None and result.baccino.confidence_interval_global is not None:
        _add_mustache_box(ax, vertical_index,
                          center=result.baccino.post_mortem_interval_global,
                          left=result.baccino.post_mortem_interval_global - result.baccino.confidence_interval_global,
                          right=result.baccino.post_mortem_interval_global + result.baccino.confidence_interval_global)
        vertical_labels.append('Baccino\n(Global)')
        vertical_index += 1

    # Idiomuscular
    if result.idiomuscular_reaction.min is not None and result.idiomuscular_reaction.max is not None:
        _plot_post_mortem_interval_result(ax, vertical_index, result.idiomuscular_reaction)
        vertical_labels.append('Idiomuscular\nreaction')
        vertical_index += 1

    # Rigor
    if result.rigor.min is not None and result.rigor.max is not None:
        _plot_post_mortem_interval_result(ax, vertical_index, result.rigor)
        vertical_labels.append('Rigor')
        vertical_index += 1

    # Lividity
    if result.lividity.min is not None and result.lividity.max is not None:
        _plot_post_mortem_interval_result(ax, vertical_index, result.lividity)
        vertical_labels.append('Lividity')
        vertical_index += 1

    # Lividity Disappearance
    if result.lividity_disappearance.min is not None and result.lividity_disappearance.max is not None:
        _plot_post_mortem_interval_result(ax, vertical_index, result.lividity_disappearance)
        vertical_labels.append('Lividity\n(Disappearance)')
        vertical_index += 1

    # Lividity Mobility
    if result.lividity_mobility.min is not None and result.lividity_mobility.max is not None:
        _plot_post_mortem_interval_result(ax, vertical_index, result.lividity_mobility)
        vertical_labels.append('Lividity\n(Mobility)')
        vertical_index += 1

    # If no plot (vertical_index is still 0)
    if vertical_index == 0:
        return None

    # --- Ticks and Labels 
    ax.set_yticks(range(vertical_index))
    ax.set_yticklabels(vertical_labels)

    tick_index = 0
    for ytick in ax.get_yticklabels():
        ytick.set_color(_pick_color(tick_index))
        tick_index += 1
        
    ax.set_ylabel('Method', labelpad=10)
    ax.set_xlabel('Estimated Post-Mortem Interval (hours)')
    ax.set_title('Comparison of Estimated Post-Mortem Intervals', pad=10)

    fig.subplots_adjust(left=0.18, bottom=0.15, top=0.9, right=0.92)
    ax.grid(True, alpha=0.3)

    # Adjust label sizes to optimize space
    ax.tick_params(axis='y', labelsize=9)
    ax.tick_params(axis='x', labelsize=8)

    # Optimize the display of values on the graph
    for text in ax.texts:
        text.set_fontsize(10)

    return fig
