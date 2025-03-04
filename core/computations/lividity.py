from core.constants import LividityType
from core.output_results import PostMortemIntervalResults

# Constants
LIVIDITY_INTERVALS = {
    LividityType.NOT_SPECIFIED: (float('nan'), float('nan')),
    LividityType.ABSENT: (0.0, 3.0),
    LividityType.DEVELOPMENT: (0.25, 3.0),
    LividityType.CONFLUENCE: (1.0, 4.0),
    LividityType.MAXIMUM: (3.0, float('inf')),
}
"""Intervals for lividity (in hours ?)"""


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

    _type = input_parameters.lividity
    if not _type or _type not in LIVIDITY_INTERVALS or _type == LividityType.NOT_SPECIFIED:
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(LIVIDITY_INTERVALS.get(_type))
