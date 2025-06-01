# core/output_results.py

from typing import Optional
from datetime import datetime
import numpy as np

from core import time_converter

class HenssgeRectalResults:

    # Constructors
    def __init__(
            self,
            post_mortem_interval: float = None,
            confidence_interval: float = None,
            thermal_quotient: float = None,
            corrective_factor: float = None,
            error_message: str = None,
            ref_dt: Optional[datetime] = None
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
        self.ref_dt = ref_dt 

    def pmi_min(self):
        return self.post_mortem_interval - self.confidence_interval
    
    def pmi_max(self):
        return self.post_mortem_interval + self.confidence_interval

    def __str__(self):
        """
        Display results as string
        """
        title = "**Henssge Rectal:**"

        if self.error_message:
            return f"{title}\n{self.error_message}"

        lines = [title]
        pmi_str = time_converter.format_pmi_range_string(
            self.pmi_min(), self.pmi_max(), self.ref_dt, self.post_mortem_interval
        )
        if self.ref_dt is not None and '[' in pmi_str:
             parts = pmi_str.split('[')
             if len(parts) == 2:
                 interval = parts[1].replace(' - ', ' / ').replace(']', '')
                 pmi_str = f"{parts[0].strip()} [{interval}]"

        label = "Estimated ToD" if self.ref_dt is not None else "Estimated PMI"
        lines.append(f"- {label}: {pmi_str.strip()}")

        if self.confidence_interval is not None:
            lines.append(f"- Confidence interval: {self.confidence_interval:.2f} hours")
        if self.thermal_quotient is not None:
            lines.append(f"- Thermal Quotient (Q): {self.thermal_quotient:.2f}")
        if self.corrective_factor is not None:
            lines.append(f"- Corrected corrective factor (Cf): {self.corrective_factor:.2f}")

        return "\n".join(lines)

class HenssgeBrainResults:
    # Constructor
    def __init__(
            self,
            post_mortem_interval: float = None,
            confidence_interval: float = None,
            error_message: str = None,
            ref_dt: Optional[datetime] = None
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
        self.ref_dt = ref_dt 

    def pmi_min(self):
        return self.post_mortem_interval - self.confidence_interval

    def pmi_max(self):
        return self.post_mortem_interval + self.confidence_interval

    def __str__(self):
        """
        Display results as string
        """
        title = "**Henssge Brain:**"
        if self.error_message:
            return f"{title}\n{self.error_message}"

        lines = [title]
        pmi_str = time_converter.format_pmi_range_string(
            self.pmi_min(), self.pmi_max(), self.ref_dt, self.post_mortem_interval
        )
        if self.ref_dt is not None and '[' in pmi_str:
             parts = pmi_str.split('[')
             if len(parts) == 2:
                 interval = parts[1].replace(' - ', ' / ').replace(']', '')
                 pmi_str = f"{parts[0].strip()} [{interval}]"

        label = "Estimated ToD" if self.ref_dt is not None else "Estimated PMI"
        lines.append(f"- {label}: {pmi_str.strip()}")
        
        if self.confidence_interval is not None:
            lines.append(f"- Confidence interval: {self.confidence_interval:.2f} hours")

        return "\n".join(lines)


class BaccinoResults:
    # Constructor
    def __init__(
            self,
            post_mortem_interval_interval: float = None,
            post_mortem_interval_global: float = None,
            confidence_interval_interval: float = None,
            confidence_interval_global: float = None,
            error_message: str = None,
            ref_dt: Optional[datetime] = None
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
        self.ref_dt = ref_dt

    def __str__(self):
        """
        Display results as string
        """
        title = "**Baccino:**"
        if self.error_message:
            return f"{title}\n{self.error_message}"

        lines = [title]
        label = "Estimated ToD" if self.ref_dt is not None else "Estimated PMI"

        # Interval Method
        if self.post_mortem_interval_interval is not None and self.confidence_interval_interval is not None:
            center_int = self.post_mortem_interval_interval
            ci_int = self.confidence_interval_interval
            min_int = max(0.0, center_int - ci_int)
            max_int = center_int + ci_int
            pmi_string_int = time_converter.format_pmi_range_string(min_int, max_int, self.ref_dt, center_int)
            if self.ref_dt is not None and '[' in pmi_string_int:
                 parts = pmi_string_int.split('[')
                 if len(parts) == 2:
                     interval = parts[1].replace(' - ', ' / ').replace(']', '')
                     pmi_string_int = f"{parts[0].strip()} [{interval}]"
            lines.append(f"- Interval Method ({label}): {pmi_string_int.strip()}")

        # Global Method
        if self.post_mortem_interval_global is not None and self.confidence_interval_global is not None:
            center_glob = self.post_mortem_interval_global
            ci_glob = self.confidence_interval_global
            min_glob = max(0.0, center_glob - ci_glob)
            max_glob = center_glob + ci_glob
            pmi_string_glob = time_converter.format_pmi_range_string(min_glob, max_glob, self.ref_dt, center_glob)
            if self.ref_dt is not None and '[' in pmi_string_glob:
                 parts = pmi_string_glob.split('[')
                 if len(parts) == 2:
                     interval = parts[1].replace(' - ', ' / ').replace(']', '')
                     pmi_string_glob = f"{parts[0].strip()} [{interval}]"
            lines.append(f"- Global Method ({label}): {pmi_string_glob.strip()}")

        return "\n".join(lines)

class PostMortemIntervalResults:
    # Constructor
    def __init__(
            self,
            name: str,
            min_max: tuple = (None, None),
            error_message: str = None,
            ref_dt: Optional[datetime] = None
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
        self.ref_dt = ref_dt

    def __str__(self):
        # Display results as string
        title = f"**{self.name}:** "
        if self.error_message:
            return f"{title}{self.error_message}"

        label = "Estimated ToD" if self.ref_dt is not None else "Estimated PMI"
        Notspecified = "Not specified"
        pmi_value_string = time_converter.format_pmi_range_string(
            self.min, self.max, self.ref_dt
        ).strip()
        if pmi_value_string == "Not specified" or not pmi_value_string: 
            return f"{title} Not specified"
        else:
            return f"{title} {label} {pmi_value_string}"

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
