from typing import Optional
import numpy as np

from core.tools import format_time


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

    def pmi_min(self):
        return self.post_mortem_interval - self.confidence_interval
    
    def pmi_max(self):
        return self.post_mortem_interval + self.confidence_interval

    def __str__(self):
        """
        Display results as string
        """
        to_str = "**Hennssge Rectal :**  \n"

        if self.error_message:
            return to_str + self.error_message

        to_str += f"Estimated PMI: {format_time(self.post_mortem_interval)} [{format_time(self.pmi_min())} - {format_time(self.pmi_max())}]  \n"
        to_str += f"Confidence interval (CI): {self.confidence_interval:.2f}  \n"
        to_str += f"Thermal Quotient (Q): {self.thermal_quotient:.2f}  \n"
        to_str += f"Corrective factor (Cf): {self.corrective_factor:.2f}"
        return to_str


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

    def pmi_min(self):
        return self.post_mortem_interval - self.confidence_interval

    def pmi_max(self):
        return self.post_mortem_interval + self.confidence_interval

    def __str__(self):
        """
        Display results as string
        """
        to_str = "**Hennssge Brain :**  \n"

        if self.error_message:
            return to_str + self.error_message

        to_str += f"Estimated PMI: {format_time(self.post_mortem_interval)} [{format_time(self.pmi_min())} - {format_time(self.pmi_max())}]  \n"
        to_str += f"Confidence interval (CI): {self.confidence_interval:.2f}"
        return to_str


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
        to_str = "**Hennssge Rectal :**  \n"

        if self.error_message:
            return to_str + self.error_message

        to_str += (f"Estimated PMI (Interval Method): {format_time(self.post_mortem_interval_interval)} "
                   f"[{format_time(self.post_mortem_interval_interval - self.confidence_interval_interval)} - {format_time(self.post_mortem_interval_interval + self.confidence_interval_interval)}]")
        to_str += "  \n"
        to_str += (f"Estimated PMI (Global Method): {format_time(self.post_mortem_interval_global)} "
                   f"[{format_time(self.post_mortem_interval_global - self.confidence_interval_global)} - {format_time(self.post_mortem_interval_global + self.confidence_interval_global)}]")
        return to_str


class PostMortemIntervalResults:
    # Constructor
    def __init__(
            self,
            name: str,
            min_max: tuple = (None, None),
            error_message: str = None
    ):
        """
        
        Parameters
        ----------
        name
        min_max : tuple
            min and max (in hours)
            
        error_message
        """
        self.name = name
        self.min = min_max[0]
        self.max = min_max[1]
        self.error_message = error_message

    def __str__(self):
        # Display results as string
        to_str = f"**{self.name}** "
        
        if self.error_message:
            return to_str + f": {self.error_message}"
        
        # Check if both values are defined and not NaN
        if self.min is not None and not np.isnan(self.min) and self.max is not None and not np.isnan(self.max):
            return to_str + f": Estimated PMI between {format_time(self.min)} and {format_time(self.max)}"
        
        # If only min is defined and not NaN
        elif self.min is not None and not np.isnan(self.min):
            return to_str + f": Estimated PMI > {format_time(self.min)}"
        
        # If only max is defined and not NaN
        elif self.max is not None and not np.isnan(self.max):
            return to_str + f": Estimated PMI < {format_time(self.max)}"
        
        # If no value is defined or all are NaN
        else:
            return to_str + ": Not specified"


class OutputResults:

    # Constructor
    def __init__(self):
        self.henssge_rectal: Optional[HenssgeRectalResults] = None
        self.henssge_brain: Optional[HenssgeBrainResults] = None
        self.baccino: Optional[BaccinoResults] = None
        self.idiomuscular_reaction: Optional[PostMortemIntervalResults] = None
        self.rigor: Optional[PostMortemIntervalResults] = None
        self.lividity: Optional[PostMortemIntervalResults] = None
        self.lividity_disappearance: Optional[PostMortemIntervalResults] = None
        self.lividity_mobility: Optional[PostMortemIntervalResults] = None
        

    def __str__(self):
        """
        Display results as string
        """
        test = "\n\n".join([
            str(self.henssge_rectal),
            str(self.henssge_brain),
            str(self.baccino),
            str(self.idiomuscular_reaction),
            str(self.rigor),
            str(self.lividity),
            str(self.lividity_disappearance),
            str(self.lividity_mobility)
        ])
        
        return test
