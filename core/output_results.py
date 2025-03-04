import Optional


class HenssgeRectalResults:

    # Constructors
    def __init__(
            self,
            post_mortem_interval: float = None,
            confidence_interval: float = None,
            thermal_quotient: float = None,
            corrective_factor: float = None,
            error_message: str = None
    ):
        """        
        Object encapsulating Henssge rectal output results
        
        Parameters
        ----------
        post_mortem_interval : float
            in hours
            
        confidence_interval : float
            in hours
            
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
            post_mortem_interval: float = None,
            confidence_interval: float = None,
            error_message: str = None
    ):
        """
        
        Parameters
        ----------
        post_mortem_interval : float
            in hours
            
        confidence_interval : float
            in hours
            
        error_message
        """
        self.confidence_interval = confidence_interval
        self.post_mortem_interval = post_mortem_interval
        self.error_message = error_message

class BaccinoResults:
    # Constructor
    def __init__(
            self,
            post_mortem_interval_interval: float = None,
            post_mortem_interval_global: float = None,
            confidence_interval_interval: float = None,
            confidence_interval_global: float = None,
            error_message: str = None
    ):
        """
        
        Parameters
        ----------
        post_mortem_interval_interval : float
            in hours
            
        post_mortem_interval_global : float
            in hours
            
        confidence_interval_interval : float
            in hours
            
        confidence_interval_global : float
            in hours
            
        error_message
        """
        self.post_mortem_interval_interval = post_mortem_interval_interval
        self.post_mortem_interval_global = post_mortem_interval_global
        self.confidence_interval_interval = confidence_interval_interval
        self.confidence_interval_global = confidence_interval_global
        self.error_message = error_message

class PostMortemIntervalResults:
    # Constructor
    def __init__(
            self,
            name: str,
            min: float = None,
            max: float = None,
            error_message: str = None
    ):
        """
        
        Parameters
        ----------
        name
        min : float
            in hours
            
        max : float
            in hours
            
        error_message
        """
        self.name = name
        self.min = min
        self.max = max
        self.error_message = error_message


class OutputResults:

    # Constructor
    def __init__(self):
        self.henssge_rectal: Optional[HenssgeRectalResults] = None
        self.henssge_brain: Optional[HenssgeBrainResults] = None
