from core.constants import LividityMobilityType, LIVIDITY_MOBILITY_INTERVALS
from core.output_results import PostMortemIntervalResults


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
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(LIVIDITY_MOBILITY_INTERVALS.get(_type))
