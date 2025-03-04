import Optional
from datetime import datetime, timedelta


class HenssgeRectalResults:

    # Constructors
    def __init__(
            self,
            post_mortem_interval: timedelta = None,
            confidence_interval: timedelta = None,
            thermal_quotient: float = float('nan'),
            corrective_factor: float = float('nan'),
            error_message: str = None
    ):
        """        
        Object encapsulating Henssge rectal output results
        
        Parameters
        ----------
        post_mortem_interval
        confidence_interval
        thermal_quotient
        corrective_factor
        error_message
        """
        self.post_mortem_interval = post_mortem_interval
        self.confidence_interval = confidence_interval
        self.thermal_quotient = thermal_quotient
        self.corrective_factor = corrective_factor
        self.error_message = error_message


class HenssgeBrainResults:
    # Constructor
    def __init__(
            self,
            post_mortem_interval: timedelta = None,
            confidence_interval: timedelta = None,
            error_message: str = None
    ):
        """
        
        Parameters
        ----------
        post_mortem_interval
        confidence_interval
        error_message
        """
        self.confidence_interval = confidence_interval
        self.post_mortem_interval = post_mortem_interval
        self.error_message = error_message


class OutputResults:

    # Constructor
    def __init__(self):
        self.henssge_rectal: Optional[HenssgeRectalResults] = None
        self.henssge_brain: Optional[HenssgeBrainResults] = None
