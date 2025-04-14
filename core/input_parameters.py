from datetime import datetime
from typing import Optional
from core.constants import IdiomuscularReactionType, RigorType, LividityType, LividityDisappearanceType, \
    LividityMobilityType, BodyCondition, EnvironmentType, SupportingBase


class InputParameters:

    # Constructor
    def __init__(
            self,
            tympanic_temperature: float = None,
            rectal_temperature: float = None,
            ambient_temperature: float = None,
            body_mass: float = None,
            body_condition: BodyCondition = None,
            environment: EnvironmentType = None,
            supporting_base: SupportingBase = None,
            idiomuscular_reaction: IdiomuscularReactionType = None,
            rigor_type: RigorType = None,
            lividity: LividityType = None,
            lividity_disappearance: LividityDisappearanceType = None,
            lividity_mobility: LividityMobilityType = None,
            user_corrective_factor: float = None,
            measurement_datetime: Optional[datetime] = None
    ):
        """
        Object encapsulating all inputs parameters needed by the core computation
        
        Parameters
        ----------
        tympanic_temperature : float
            Measured tympanic temperature (in °C)
        
        rectal_temperature : float
            Measured rectal temperature (in °C)
            
        ambient_temperature : float
            Ambient temperature (in °C)
            
        body_mass : float
            Body mass (in kg)
                  
        body_condition : BodyCondition        
        environment : EnvironmentType
        supporting_base : SupportingBase
        idiomuscular_reaction : IdiomuscularReactionType
        rigor_type : RigorType
        lividity : LividityType
        lividity_disappearance : LividityDisappearanceType
        lividity_mobility : LividityMobilityType
        user_corrective_factor : float
        measurement_datetime : Optional[datetime] = Optional date and time when measurements were taken.
        """
        self.tympanic_temperature = tympanic_temperature
        self.rectal_temperature = rectal_temperature
        self.ambient_temperature = ambient_temperature
        self.body_mass = body_mass
        self.body_condition = body_condition
        self.environment = environment
        self.supporting_base = supporting_base
        self.idiomuscular_reaction = idiomuscular_reaction
        self.rigor_type = rigor_type
        self.lividity = lividity
        self.lividity_disappearance = lividity_disappearance
        self.lividity_mobility = lividity_mobility
        self.user_corrective_factor = user_corrective_factor
        self.measurement_datetime = measurement_datetime

    def __str__(self):
        members = []
        if self.measurement_datetime:
            from .datetime_utils import format_datetime
            members.append(f"measurement_datetime = {format_datetime(self.measurement_datetime)}")
        if self.tympanic_temperature:
            members.append(f"tympanic_temperature = {self.tympanic_temperature}°C")
        if self.rectal_temperature:
            members.append(f"rectal_temperature = {self.rectal_temperature}°C")
        if self.ambient_temperature:
            members.append(f"ambient_temperature = {self.ambient_temperature}°C")
        if self.body_mass:
            members.append(f"body_mass = {self.body_mass}kg")
        if self.environment:
            members.append(f"environment = {self.environment}")
        if self.supporting_base:
            members.append(f"supporting_base = {self.supporting_base}")
        if self.idiomuscular_reaction:
            members.append(f"idiomuscular_type = {self.idiomuscular_reaction}")
        if self.rigor_type:
            members.append(f"rigor_type = {self.rigor_type}")
        if self.lividity:
            members.append(f"lividity_type = {self.lividity}")
        if self.lividity_disappearance:
            members.append(f"lividity_disappearance = {self.lividity_disappearance}")
        if self.lividity_mobility:
            members.append(f"lividity_mobility = {self.lividity_mobility}")
        if self.user_corrective_factor:
            members.append(f"user_corrective_factor = {self.user_corrective_factor}")
            
        return '\n'.join(members)
