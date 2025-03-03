from core.constants import IdiomuscularReactionType, RigorType, LividityType, LividityDisappearanceType, \
    LividityMobilityType, BodyCondition, EnvironmentType, SupportingBase, TEMPERATURE_LIMITS, TemperatureLimitsType, BODY_MASS_LIMIT


class InputParameters:

    # Constructor
    def __init__(
            self,
            tympanic_temperature: float,
            rectal_temperature: float,
            ambient_temperature: float,
            body_mass: float,
            body_condition: BodyCondition,
            environment: EnvironmentType,
            supporting_base: SupportingBase,
            idiomuscular_type: IdiomuscularReactionType,
            rigor_type: RigorType,
            lividity_type: LividityType,
            lividity_disappearance: LividityDisappearanceType,
            lividity_mobility: LividityMobilityType,
            user_corrective_factor: float = float('nan')
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
        idiomuscular_type : IdiomuscularReactionType
        rigor_type : RigorType
        lividity_type : LividityType
        lividity_disappearance : LividityDisappearanceType
        lividity_mobility : LividityMobilityType
        user_corrective_factor : float
        """
        self.tympanic_temperature = tympanic_temperature
        self.rectal_temperature = rectal_temperature
        self.ambient_temperature = ambient_temperature
        self.body_mass = body_mass
        self.body_condition = body_condition
        self.environment = environment
        self.supporting_base = supporting_base
        self.idiomuscular_type = idiomuscular_type
        self.rigor_type = rigor_type
        self.lividity_type = lividity_type
        self.lividity_disappearance = lividity_disappearance
        self.lividity_mobility = lividity_mobility
        self.user_corrective_factor = user_corrective_factor

    def validate(self) -> bool:
        """
        Validation of members of input parameters
        
        Returns
        -------
        True 
            if inputs are valid
        
        Raises
        -------
        ValueError
            if some inputs are not valid        
        """

        error_message = []

        # Verification of temperature limits
        ambient_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.AMBIENT)
        if not (ambient_limits[0] <= self.ambient_temperature <= ambient_limits[1]):
            error_message.append(f"The ambient temperature ({self.ambient_temperature}°C) is not valid and must be between {ambient_limits[0]}°C and {ambient_limits[1]}°C.")

        rectal_limits = TEMPERATURE_LIMITS.get(TemperatureLimitsType.RECTAL)
        if not (rectal_limits[0] <= self.rectal_temperature <= rectal_limits[1]):
            error_message.append(f"The rectal temperature ({self.rectal_temperature}°C) is not valid and must be between {rectal_limits[0]}°C and {rectal_limits[1]}°C.")

        # Verification of body mass limits
        if not (BODY_MASS_LIMIT[0] <= self.body_mass <= BODY_MASS_LIMIT[1]):
            error_message.append(f"The body mass ({self.body_mass}kg) is not valid and must be between {BODY_MASS_LIMIT[0]}kg and {BODY_MASS_LIMIT[1]}kg.")

        # Raise error if some values are not valid
        if len(error_message) > 0:
            raise ValueError('\n'.join(error_message))

        # Returns true if everything is valid
        return True
