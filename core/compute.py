# core/compute.py

from core.computations import henssge_rectal, henssge_brain, baccino, idiomuscular_reaction, lividity, lividity_disappearance, lividity_mobility, rigor
from core.input_parameters import InputParameters
from core.output_results import OutputResults


def run(input_parameters: InputParameters) -> OutputResults:
    """
    Compute using different methods for estimating the post-mortem interval (PMI).
    It also handles errors and warnings in case of missing or unusable values.
    The threshold values and ranges are taken from the book "Time of Death" by Madea.

    The function uses the following methods to estimate the PMI:
    - Henssge Method (Rectal)
    - Henssge Method (Brain)
    - Baccino Method
    - Idiomuscular Reaction
    - Rigor Mortis
    - Livor Mortis
    - Disappearance of Livor Mortis
    - Livor Mortis Mobility
    """

    results = OutputResults()

    # Henssge rectal computation
    results.henssge_rectal = henssge_rectal.compute(input_parameters)

    # Henssge brain computation
    results.henssge_brain = henssge_brain.compute(input_parameters)

    # Baccino computation
    results.baccino = baccino.compute(input_parameters)

    # Idiomuscular reaction
    results.idiomuscular_reaction = idiomuscular_reaction.compute(input_parameters)

    # Lividity
    results.lividity = lividity.compute(input_parameters)

    # Lividity Disappearance
    results.lividity_disappearance = lividity_disappearance.compute(input_parameters)

    # Lividity Mobility
    results.lividity_mobility = lividity_mobility.compute(input_parameters)

    # Rigor
    results.rigor = rigor.compute(input_parameters)

    # --- Return
    return results
