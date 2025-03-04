from core.constants import IdiomuscularReactionType, IDIOMUSCULAR_REACTION_INTERVALS
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

    _type = input_parameters.idiomuscular_type
    if not _type or _type not in IDIOMUSCULAR_REACTION_INTERVALS or _type == IdiomuscularReactionType.NOT_SPECIFIED:
        return PostMortemIntervalResults(error_message="Not Specified")

    return PostMortemIntervalResults(IDIOMUSCULAR_REACTION_INTERVALS.get(_type))
