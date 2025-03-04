from core.constants import LividityDisappearanceType, LIVIDITY_DISAPPERANCE_INTERVALS
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

    _type = input_parameters.lividity_disappearance
    if not _type or _type not in LIVIDITY_DISAPPERANCE_INTERVALS or _type == LividityDisappearanceType.NOT_SPECIFIED:
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(LIVIDITY_DISAPPERANCE_INTERVALS.get(_type))
