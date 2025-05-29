# core/time_converter.py

import math
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .tools import format_time as format_relative_time

# --- Configuration ---
# This variable will hold the reference datetime if provided by the user.
_reference_datetime: Optional[datetime] = None

# --- Public Functions ---

def set_reference_datetime(ref_dt: Optional[datetime]) -> None:
    """Sets the global reference datetime for calculations."""
    global _reference_datetime
    _reference_datetime = ref_dt

def get_reference_datetime() -> Optional[datetime]:
    """Gets the currently set global reference datetime."""
    return _reference_datetime

def format_absolute_datetime(dt: Optional[datetime]) -> str:
    """Formats a datetime object into 'DD/MM/YYYY - HHhMM'."""
    if dt is None:
        return "N/A" # Not Applicable or Not Available
    try:
        # Format: DD/MM/YYYY - HHhMM
        return dt.strftime("%d/%m/%Y - %Hh%M")
    except ValueError:
        # Handle potential issues with very large/small dates if necessary
        return "Invalid Date"

def calculate_absolute_dt(pmi_hours: Optional[float]) -> Optional[datetime]:
    """
    Calculates the absolute datetime of death based on the reference time
    and the post-mortem interval in hours.

    Args:
        pmi_hours: The post-mortem interval in hours.

    Returns:
        The calculated absolute datetime of death, or None if calculation
        is not possible (no reference time, infinite/NaN PMI).
    """
    if _reference_datetime is None or pmi_hours is None or math.isnan(pmi_hours) or math.isinf(pmi_hours):
        return None
    try:
        # Time of death = Reference Time - PMI
        return _reference_datetime - timedelta(hours=pmi_hours)
    except (OverflowError, ValueError):
        # Handle potential errors with very large timedelta values
        return None

# --- Main formatting function for text (run.py) ---
def format_pmi_range_string(
    pmi_min_hours: Optional[float],
    pmi_max_hours: Optional[float],
    pmi_center_hours: Optional[float] = None,
    prefix: str = "Estimated PMI"
) -> str:
    """
    Formats a PMI range (min, max, optional center) into a string.
    Uses absolute dates if a reference datetime is set, otherwise uses relative hours.

    Args:
        pmi_min_hours: Minimum PMI in hours. Can be 0 or NaN.
        pmi_max_hours: Maximum PMI in hours. Can be infinity or NaN.
        pmi_center_hours: Optional central estimate PMI in hours.
        prefix: The text to put before the formatted range (e.g., "Estimated PMI").

    Returns:
        A formatted string representing the PMI.
    """
    # Handle NaN cases (equivalent to "Not Specified" in original code)
    min_is_nan = pmi_min_hours is None or math.isnan(pmi_min_hours)
    max_is_nan = pmi_max_hours is None or math.isnan(pmi_max_hours)

    if min_is_nan and max_is_nan:
        return f"{prefix}: Not specified"

    # If no reference time, use original relative formatting
    if _reference_datetime is None:
        min_rel = format_relative_time(pmi_min_hours if not min_is_nan else 0) # Treat NaN min as 0 for display logic
        max_rel = format_relative_time(pmi_max_hours if not max_is_nan else float('inf')) # Treat NaN max as inf
        center_rel = format_relative_time(pmi_center_hours) if pmi_center_hours is not None else None

        if not min_is_nan and not max_is_nan and not math.isinf(pmi_max_hours) and not math.isclose(pmi_min_hours, 0.0):
            # Standard interval: XhY - WhZ
            range_str = f"{min_rel} - {max_rel}"
            if center_rel:
                 # Optionally add center: 5h30 [3h00 - 8h00] (Example)
                 # Let's follow the text output format: keep range only for interval results
                 pass # Keep range_str as is for interval signs
            if pmi_center_hours is not None: # For Henssge/Baccino like results
                 return f"{prefix} {center_rel} [{min_rel} - {max_rel}]"
            else: # For interval signs
                 return f"{prefix} between {min_rel} and {max_rel}"
        elif not min_is_nan and (max_is_nan or math.isinf(pmi_max_hours)):
            return f"{prefix} > {min_rel}"
        elif (min_is_nan or math.isclose(pmi_min_hours, 0.0)) and not max_is_nan and not math.isinf(pmi_max_hours):
            return f"{prefix} < {max_rel}"
        else:
            return f"{prefix}: Interval undefined ({min_rel} - {max_rel})"
        
    else: # Absolute Time Calculation
        dt_latest = calculate_absolute_dt(pmi_min_hours)
        dt_earliest = calculate_absolute_dt(pmi_max_hours)
        dt_center = calculate_absolute_dt(pmi_center_hours) if pmi_center_hours is not None else None

        fmt_latest = format_absolute_datetime(dt_latest)
        fmt_earliest = format_absolute_datetime(dt_earliest)
        fmt_center = format_absolute_datetime(dt_center) if dt_center else None

        has_earliest = dt_earliest is not None and fmt_earliest not in ["N/A", "Invalid Date"]
        has_latest = dt_latest is not None and fmt_latest not in ["N/A", "Invalid Date"]
        has_center = dt_center is not None and fmt_center not in ["N/A", "Invalid Date"]

    # Build the output string
        if has_earliest and has_latest:
            # Full range: [Earliest Date] - [Latest Date]
            range_str = f"Between {fmt_earliest} and {fmt_latest}"
            if has_center:
                return f"{prefix} {fmt_center} [{fmt_earliest} | {fmt_latest}]"
            else: # For interval signs
                return f"{prefix} {range_str}"
        elif has_earliest and not has_latest: # Only earliest makes sense (PMI < max_hours => After earliest)
            return f"{prefix}: After {fmt_earliest}"
        elif not has_earliest and has_latest: # Only latest makes sense (PMI > min_hours => Before latest)
            return f"{prefix}: Before {fmt_latest}"
        else:
            return f"{prefix}: Cannot determine absolute time"

# --- Function for Plot ---

def format_plot_scatter_label(pmi_hours: Optional[float]) -> str:
    """Formats a label for a single point (scatter) on a plot."""
    if pmi_hours is None or math.isnan(pmi_hours):
        return "N/A"

    if _reference_datetime is None:
        return f"{format_relative_time(pmi_hours)}"
    else:
        dt = calculate_absolute_dt(pmi_hours)
        return f"{format_absolute_datetime(dt)}"

def format_plot_ci_label(pmi_min_hours: Optional[float], pmi_max_hours: Optional[float]) -> str:
    """Formats a label for a confidence interval (axvspan) on a plot."""
    if pmi_min_hours is None or math.isnan(pmi_min_hours) or \
       pmi_max_hours is None or math.isnan(pmi_max_hours):
        return "CI: N/A"

    if _reference_datetime is None:
        min_rel = format_relative_time(pmi_min_hours)
        max_rel = format_relative_time(pmi_max_hours)
        return f"CI: {min_rel} - {max_rel}"
    else:
        # Remember: Min PMI hours -> Latest possible death time
        #           Max PMI hours -> Earliest possible death time
        hour_format = "%Hh%M"
        dt_latest = calculate_absolute_dt(pmi_min_hours)
        dt_earliest = calculate_absolute_dt(pmi_max_hours)
        fmt_earliest = dt_earliest.strftime(hour_format) if dt_earliest else "N/A"
        fmt_latest = dt_latest.strftime(hour_format) if dt_latest else "N/A"
        return f"{fmt_earliest} - {fmt_latest}"

def format_plot_xlabel() -> str:
    """Returns the appropriate X-axis label based on reference time."""
    if _reference_datetime is None:
        return "Estimated Post-Mortem Interval (hours)"
    else:
        return "Estimated Time of Death (position relative to measurement time)"

def generate_plot_x_tick_labels(tick_hours: list[float]) -> list[str]:
    """
    Generates labels for X-axis ticks on plots.
    Returns relative hours if no reference datetime is set.
    Returns absolute Date+Hour if reference is set, showing the date
    only on the first tick and when the date changes.

    Args:
        tick_hours: A list of tick positions in hours PMI.

    Returns:
        A list of strings to be used as tick labels.
    """
    if not tick_hours:
        return []

    if _reference_datetime is None:
        # Relative mode: Simply return hours in standard string format
        return [format_relative_time(h) for h in tick_hours]
    else:
        # Absolute mode: returns absolute date and hours
        output_labels = []
        last_date_str = None # Save the last date displayed

        for hour in tick_hours:
            if hour < 0: # Do not attempt to calculate for negative ticks (e.g. xlim left=-1)
                output_labels.append("")
                continue

            dt = calculate_absolute_dt(hour)
            if dt is None:
                output_labels.append("") # Leave blank if not calculable
                continue

            # Format date and time parts
            current_date_str = dt.strftime("%d/%m/%Y")
            hour_str = dt.strftime("%Hh%M") # Hour format only

            # Decide what to display
            if last_date_str is None or current_date_str != last_date_str:
                # First time or date change: display Date + Time
                # Use \n to separate on two lines if necessary
                label = f"{hour_str}\n{current_date_str}"
                last_date_str = current_date_str # Update last viewed date
            else:
                # Same date as previous: show time only
                label = hour_str

            output_labels.append(label)

        return output_labels
    
def format_plot_mustache_labels(pmi_min: Optional[float], pmi_max: Optional[float], pmi_center: Optional[float]) -> Tuple[str, str, str]:
    """
    Formats labels specifically for the mustache box plot helper.
    Returns (center_label, left_label, right_label)
    """
    center_label, left_label, right_label = "N/A", "N/A", "N/A"
    has_center = pmi_center is not None and not math.isnan(pmi_center)
    has_min = pmi_min is not None and not math.isnan(pmi_min)
    has_max = pmi_max is not None and not math.isnan(pmi_max)

    if _reference_datetime is None:
        # Format relatif
        center_str = format_relative_time(pmi_center) if has_center else ""
        left_str = format_relative_time(pmi_min) if has_min else ""
        right_str = format_relative_time(pmi_max) if has_max else ""
        center_label = f"{center_str}" if center_str else ""
        left_label = left_str
        right_label = right_str
    else:
        # Format absolu
        dt_center = calculate_absolute_dt(pmi_center) if has_center else None
        dt_latest = calculate_absolute_dt(pmi_min) if has_min else None    # Min hours -> latest death
        dt_earliest = calculate_absolute_dt(pmi_max) if has_max else None # Max hours -> earliest death
        hour_format = "%Hh%M"

        center_str = format_absolute_datetime(dt_center) if dt_center else ""
        fmt_earliest = dt_earliest.strftime(hour_format) if dt_earliest else ""
        fmt_latest = dt_latest.strftime(hour_format) if dt_latest else ""

        center_label = f"{center_str}" if center_str else ""
        left_label = fmt_latest # Left text = earliest date
        right_label = fmt_earliest  # Right text = most recent date

    return center_label, left_label, right_label


def format_plot_zone_label(pmi_limit: Optional[float], side: str) -> Tuple[str, str]:
    """
    Formats labels specifically for the zone box plot helper.
    Returns (text_label, horizontal_alignment)
    """
    if pmi_limit is None or math.isnan(pmi_limit):
        return "N/A", "center"

    text_label, align = "N/A", "center"

    if _reference_datetime is None:
        # Format relatif
        formatted_pos = format_relative_time(pmi_limit)
        if side == 'upper': # PMI > limit
            text_label, align = f"PMI > {formatted_pos}", 'left'
        elif side == 'lower': # PMI < limit
            text_label, align = f"PMI < {formatted_pos}", 'right'
    else:
        # Format absolu
        dt_limit = calculate_absolute_dt(pmi_limit)
        formatted_dt = format_absolute_datetime(dt_limit)
        if formatted_dt not in ["N/A", "Invalid Date"]:
            if side == 'upper': # PMI > limit => Death Before dt_limit
                text_label, align = f"ToD Before {formatted_dt}", 'right'
            elif side == 'lower': # PMI < limit => Death After dt_limit
                text_label, align = f"ToD After {formatted_dt}", 'left'

    return text_label, align

