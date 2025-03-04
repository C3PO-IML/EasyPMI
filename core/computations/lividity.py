from core.constants import LIVIDITY_INTERVALS, LividityType
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

    _type = input_parameters.lividity_type
    if not _type or _type not in LIVIDITY_INTERVALS or _type == LividityType.NOT_SPECIFIED:
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(LIVIDITY_INTERVALS.get(_type))
