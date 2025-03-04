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

    def __str__(self):
        """
        Display results as string
        """
        to_str = "**Hennssge Rectal :**\n"

        if not self.error_message:
            return to_str + self.error_message

        to_str += (f"Estimated PMI (Interval Method): {format_time(self.post_mortem_interval_interval)} "
                   f"[{format_time(self.post_mortem_interval_interval - self.confidence_interval_interval)} - {format_time(self.post_mortem_interval_interval + self.confidence_interval_interval)}]")
        to_str += "\n"
        to_str += (f"Estimated PMI (Global Method): {format_time(self.post_mortem_interval_global)} "
                   f"[{format_time(self.post_mortem_interval_global - self.confidence_interval_global)} - {format_time(self.post_mortem_interval_global + self.confidence_interval_global)}]")


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

    def __str__(self):
        """
        Display results as string
        """
        to_str = f"**{self.name} :**\n"

        if self.min and np.isclose(self.min, 0.0) and self.max and self.max != float('inf'):
            return to_str + f"Estimated PMI [{format_time(self.min)} - {format_time(self.max)}]"

        if not self.min or np.isclose(self.min, 0.0):
            return to_str + f"Estimated PMI < {format_time(self.max)}"

        if not self.max or self.max == float('inf'):
            return to_str + f"Estimated PMI > {format_time(self.min)}"

        return to_str + "Not specified"


class OutputResults:

    # Constructor
    def __init__(self):
        self.henssge_rectal: Optional[HenssgeRectalResults] = None
        self.henssge_brain: Optional[HenssgeBrainResults] = None
        self.baccino = Optional[BaccinoResults] = None
        self.idiomuscular_reaction = Optional[PostMortemIntervalResults] = None
        self.lividity = Optional[PostMortemIntervalResults] = None
        self.lividity_disappearance = Optional[PostMortemIntervalResults] = None
        self.lividity_mobility = Optional[PostMortemIntervalResults] = None
        self.rigor = Optional[PostMortemIntervalResults] = None

