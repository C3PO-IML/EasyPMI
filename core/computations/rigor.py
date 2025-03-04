from core.constants import RigorType, RIGIDITY_INTERVALS
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

    _type = input_parameters.rigor_type
    if not _type or _type not in RIGIDITY_INTERVALS or _type == RigorType.NOT_SPECIFIED:
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(RIGIDITY_INTERVALS.get(_type))
