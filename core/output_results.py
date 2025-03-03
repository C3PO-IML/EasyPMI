import Optional
from datetime import datetime, timedelta


class HenssgeRectalResults:
    
    # Constructors
    def __init__(
            self,
            estimated_death_time: datetime = None,
            confidence_interval: timedelta = None,
            thermal_quotient: float = float('nan'),
            error_message: str = None
    ):
        """        
        Object encapsulating Henssge rectal output results
        
        Parameters
        ----------
        estimated_death_time
        confidence_interval
        thermal_quotient
        """
        self.estimated_death_time = estimated_death_time
        self.confidence_interval = confidence_interval
        self.thermal_quotient = thermal_quotient
        self.error_message = None


class HenssgeBrainResults:
    # Constructor
    def __init__(
            self,
            estimated_death_time: datetime,
            confidence_interval: timedelta,
            thermal_quotient: float
    ):
        """
        
        Parameters
        ----------
        estimated_death_time
        confidence_interval
        thermal_quotient
        """
        self.thermal_quotient = thermal_quotient
        self.confidence_interval = confidence_interval
        self.estimated_death_time = estimated_death_time


class OutputResults:

    # Constructor
    def __init__(self):
        self.henssge_rectal: Optional[HenssgeRectalResults] = None
