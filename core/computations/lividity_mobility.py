from core.constants import LividityMobilityType
from core.output_results import PostMortemIntervalResults

# Constants
LIVIDITY_MOBILITY_INTERVALS = {
    LividityMobilityType.NOT_SPECIFIED: (float('nan'), float('nan')),
    LividityMobilityType.COMPLETE: (0.0, 6.0),
    LividityMobilityType.PARTIAL: (4.0, 24.0),
    LividityMobilityType.LITTLE_PALOR_ONLY: (10.0, float('inf')),
}
"""Intervals for lividity mobility (in hours ?)"""

NAME = "Lividity Mobility"


# Main computation
def compute(input_parameters) -> PostMortemIntervalResults:
    """
    
    Parameters
    ----------
    input_parameters : InputParameters

    Returns
    -------
    PostMortemIntervalResults

    """

    _type = input_parameters.lividity_mobility
    if not _type or _type not in LIVIDITY_MOBILITY_INTERVALS or _type == LividityMobilityType.NOT_SPECIFIED:
        return PostMortemIntervalResults(NAME, error_message="Not Specified")

    return PostMortemIntervalResults(NAME, LIVIDITY_MOBILITY_INTERVALS.get(_type))
