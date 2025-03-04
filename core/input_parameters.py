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
            idiomuscular_type: IdiomuscularReactionType = None,
            rigor_type: RigorType = None,
            lividity_type: LividityType = None,
            lividity_disappearance: LividityDisappearanceType = None,
            lividity_mobility: LividityMobilityType = None,
            user_corrective_factor: float = None
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
