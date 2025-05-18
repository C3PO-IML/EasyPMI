# core/tools.py

import math

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
    # verifying if the time is NaN or infinite
    if math.isnan(time):
        return "NaN"
    if math.isinf(time):
        return "∞" 
    
    # Formating the time
    if time == float('inf'):
        return "∞"
    hours = int(time)
    minutes = int((time - hours) * 60)
    return f"{hours}h{minutes:02}"