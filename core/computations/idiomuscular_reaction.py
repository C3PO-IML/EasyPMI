from core.constants import IdiomuscularReactionType
from core.output_results import PostMortemIntervalResults

# Constants
IDIOMUSCULAR_REACTION_INTERVALS = {
    IdiomuscularReactionType.NOT_SPECIFIED: (float('nan'), float('nan')),
    IdiomuscularReactionType.ZSAKO: (0.0, 3.0),
    IdiomuscularReactionType.STRONG_REVERSIBLE: (0.0, 5.5),
    IdiomuscularReactionType.WEAK_PERSISTENT: (1.5, 13.0),
    IdiomuscularReactionType.NO_REACTION: (1.5, float('inf')),
}
"""Intervals for idiomuscular reactions (in hours ?)"""

NAME = "Idiomuscular Reaction"

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

    _type = input_parameters.idiomuscular_reaction
    if not _type or _type not in IDIOMUSCULAR_REACTION_INTERVALS or _type == IdiomuscularReactionType.NOT_SPECIFIED:
        return PostMortemIntervalResults(NAME, error_message="Not Specified")

    return PostMortemIntervalResults(NAME, IDIOMUSCULAR_REACTION_INTERVALS.get(_type))
