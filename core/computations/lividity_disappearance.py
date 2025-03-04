from core.constants import LividityDisappearanceType
from core.output_results import PostMortemIntervalResults

# Constants
LIVIDITY_DISAPPEARANCE_INTERVALS = {
    LividityDisappearanceType.NOT_SPECIFIED: (float('nan'), float('nan')),
    LividityDisappearanceType.COMPLETE: (0.0, 20.0),
    LividityDisappearanceType.INCOMPLETE: (10.0, float('inf')),
}
"""Intervals for lividity disappearance (in hours ?)"""

NAME = "Lividity Disappearance"


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

    _type = input_parameters.lividity_disappearance
    if not _type or _type not in LIVIDITY_DISAPPEARANCE_INTERVALS or _type == LividityDisappearanceType.NOT_SPECIFIED:
        return PostMortemIntervalResults(NAME, error_message="Not Specified")

    return PostMortemIntervalResults(NAME, LIVIDITY_DISAPPEARANCE_INTERVALS.get(_type))
