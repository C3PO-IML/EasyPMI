from core.constants import RigorType
from core.output_results import PostMortemIntervalResults

# Constants
RIGOR_INTERVALS = {
    RigorType.NOT_SPECIFIED: (float('nan'), float('nan')),
    RigorType.NOT_ESTABLISHED: (0.0, 7.0),
    RigorType.POSSIBLE_REESTABLISHMENT: (0.5, 9.5),
    RigorType.COMPLETE_RIGIDITY: (2.0, 20.0),
    RigorType.PERSISTENCE: (24.0, 96.0),
    RigorType.RESOLUTION: (24.0, float('inf')),
}
"""Intervals for rigor (in hours ?)"""

NAME = "Rigor"


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

    _type = input_parameters.rigor_type
    if not _type or _type not in RIGOR_INTERVALS or _type == RigorType.NOT_SPECIFIED:
        return PostMortemIntervalResults(NAME, error_message="Not Specified")

    return PostMortemIntervalResults(NAME, RIGOR_INTERVALS.get(_type))
