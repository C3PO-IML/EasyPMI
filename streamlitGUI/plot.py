import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import streamlit as st
from core.tools import format_time


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
            temperatures.append(
                t_ambient + (37.2 - t_ambient) * (1.25 * np.exp(-(1.2815 / M_corrige ** 0.625 - 0.0284) * t) - 0.25 * np.exp(-5 * (1.2815 / M_corrige ** 0.625 - 0.0284) * t)))
        else:
            temperatures.append(
                t_ambient + (37.2 - t_ambient) * (1.11 * np.exp(-(1.2815 / M_corrige ** 0.625 - 0.0284) * t) - 0.11 * np.exp(-10 * (1.2815 / M_corrige ** 0.625 - 0.0284) * t)))

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


def plot_comparative_pmi_results(corrected_pmi: float, t_min: float, t_max: float, corrected_pmi_brain: float, t_min_brain: float, t_max_brain: float, PMI_interval: float,
                                 PMI_global: float, CI_interval: float, CI_global: float, pmi_idiomuscular_reaction_min: float, pmi_idiomuscular_reaction_max: float,
                                 pmi_rigor_min: float, pmi_rigor_max: float, pmi_lividity_min: float, pmi_lividity_max: float, pmi_lividity_disappearance_min: float,
                                 pmi_lividity_disappearance_max: float, pmi_lividity_mobility_min: float, pmi_lividity_mobility_max: float) -> Figure:
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
    values = [v for v in [t_max, t_max_brain, PMI_interval, PMI_global, pmi_idiomuscular_reaction_max, pmi_rigor_max, pmi_lividity_max, pmi_lividity_disappearance_max,
                          pmi_lividity_mobility_max] if v is not None]
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
            ax.errorbar([(pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2], [4],
                        xerr=[[(pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2 - pmi_idiomuscular_reaction_min],
                              [pmi_idiomuscular_reaction_max - (pmi_idiomuscular_reaction_min + pmi_idiomuscular_reaction_max) / 2]], fmt='none', color='purple')
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
            ax.errorbar([(pmi_rigor_min + pmi_rigor_max) / 2], [5],
                        xerr=[[(pmi_rigor_min + pmi_rigor_max) / 2 - pmi_rigor_min], [pmi_rigor_max - (pmi_rigor_min + pmi_rigor_max) / 2]], fmt='none', color='orange')
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
            ax.errorbar([(pmi_lividity_min + pmi_lividity_max) / 2], [6],
                        xerr=[[(pmi_lividity_min + pmi_lividity_max) / 2 - pmi_lividity_min], [pmi_lividity_max - (pmi_lividity_min + pmi_lividity_max) / 2]], fmt='none',
                        color='brown')
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
            ax.errorbar([(pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2], [8],
                        xerr=[[(pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2 - pmi_lividity_mobility_min],
                              [pmi_lividity_mobility_max - (pmi_lividity_mobility_min + pmi_lividity_mobility_max) / 2]], fmt='none', color='magenta')
            bar_height = add_vertical_bars(ax, pmi_lividity_mobility_min, pmi_lividity_mobility_max, 8, 'magenta')
            add_interval_values(ax, pmi_lividity_mobility_min, pmi_lividity_mobility_max, 8, bar_height, 'magenta')

    ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_yticklabels(
        ['Henssge (Rectal)', 'Henssge (Brain)', 'Baccino\n(Interval)', 'Baccino\n(Global)', 'Idiomuscular\nreaction', 'Rigor', 'Lividity', 'Lividity\n(Disappearance)',
         'Lividity\n(Mobility)'])
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
