# core/datetime_utils.py
from datetime import datetime, timedelta, date, time
from typing import Optional, Tuple
import numpy as np
import math

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def combine_date_time(d: Optional[date], t: Optional[time]) -> Optional[datetime]:
    """Combines date and time objects into a datetime object."""
    if d is not None and t is not None:
        return datetime.combine(d, t)
    return None

def subtract_hours_from_datetime(dt: Optional[datetime], hours: Optional[float]) -> Optional[datetime]:
    """Subtracts hours (can be float) from a datetime object."""
    if dt is None or hours is None or math.isnan(hours) or math.isinf(hours):
        return None
    delta = timedelta(hours=hours)
    return dt - delta

def format_datetime(dt: Optional[datetime], fmt: str = DEFAULT_DATETIME_FORMAT) -> str:
    """Formats a datetime object into a string."""
    if dt is None:
        return "N/A"
    return dt.strftime(fmt)

def format_pmi_absolute(measurement_dt: Optional[datetime],
                        pmi_min_hours: Optional[float],
                        pmi_max_hours: Optional[float],
                        pmi_estimate_hours: Optional[float] = None) -> str:
    """
    Formats the PMI result as an absolute date/time range if measurement_dt is provided.
    Falls back to relative time formatting otherwise.

    Returns:
        Formatted string representing the PMI range (and estimate if provided).
    """
    # Use relative time formatting from core.tools if no measurement time
    if measurement_dt is None:
        from core.tools import format_time # Local import to avoid circular dependency if moved
        min_str = format_time(pmi_min_hours) if pmi_min_hours is not None and not math.isnan(pmi_min_hours) else "?"
        max_str = format_time(pmi_max_hours) if pmi_max_hours is not None and not math.isnan(pmi_max_hours) else "?"
        estimate_str = format_time(pmi_estimate_hours) if pmi_estimate_hours is not None and not math.isnan(pmi_estimate_hours) else None

        range_str = f"Between {min_str} and {max_str}"
        if estimate_str:
            return f"Estimate: {estimate_str} [{range_str}]"
        else:
            # Handle single-sided intervals for signs
            if min_str == "0h00" and max_str != "?" and max_str != "∞":
                return f"PMI < {max_str}"
            elif max_str == "∞" and min_str != "?" and min_str != "0h00":
                 return f"PMI > {min_str}"
            elif min_str == "?" and max_str == "?":
                 return "Not Specified"
            else:
                return range_str


    # Calculate absolute datetimes
    # Note: We subtract PMI from measurement time to get time of death
    end_dt = subtract_hours_from_datetime(measurement_dt, pmi_max_hours)
    start_dt = subtract_hours_from_datetime(measurement_dt, pmi_min_hours)
    estimate_dt = subtract_hours_from_datetime(measurement_dt, pmi_estimate_hours)

    # Format absolute datetimes
    start_str = format_datetime(start_dt)
    end_str = format_datetime(end_dt)
    estimate_str = format_datetime(estimate_dt)

    # Handle infinite cases (e.g., for signs)
    if pmi_max_hours == float('inf') and pmi_min_hours is not None and not np.isclose(pmi_min_hours, 0.0):
        # PMI > min_hours -> Death occurred *before* start_dt
        return f"Before {start_str}"
    elif np.isclose(pmi_min_hours, 0.0) and pmi_max_hours is not None and pmi_max_hours != float('inf'):
        # PMI < max_hours -> Death occurred *after* end_dt
        return f"After {end_str}"
    elif start_dt is None and end_dt is None:
         return "Not Specified"
    elif start_dt is None or end_dt is None: # Should ideally not happen if min/max are valid numbers
         return f"Between {start_str} and {end_str}" # Will show N/A for one side

    # Format final string
    range_str = f"Between {end_str} and {start_str}" # Earlier date first
    if estimate_dt:
        return f"Estimate: {estimate_str} [{range_str}]"
    else:
        return range_str