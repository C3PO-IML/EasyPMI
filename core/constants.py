from enum import Enum, auto


# --- Enumerations
# --------------------------------

class TemperatureLimitsType(Enum):
    """Types of temperature limits"""

    TYMPANIC = auto()
    """Tympanic"""

    RECTAL = auto()
    """Rectal"""

    AMBIENT = auto()
    """Ambient"""


class BodyCondition(Enum):
    """Conditions in which the body was found"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    NAKED = auto()
    """Naked"""

    LIGHTLY = auto()
    """Lightly dressed (one to two thin layers)"""

    MODERATELY = auto()
    """Moderately dressed (two to three thin layers)"""

    WARMLY = auto()
    """Warmly dressed (thick layers)"""

    HEAVILY = auto()
    """Very dressed (thick blanket)"""


class EnvironmentType(Enum):
    """Environment in which the body was found"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    STILL_AIR = auto()
    """Still air"""

    MOVING_AIR = auto()
    """Moving air"""

    WET_STILL_AIR = auto()
    """Wet and still air"""

    WET_MOVING_AIR = auto()
    """Wet and moving air"""

    STILL_WATER = auto()
    """Still water"""

    FLOWING_WATER = auto()
    """Flowing water"""


class SupportingBase(Enum):
    """Supporting base on which the body was found"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    INDIFFERENT = auto()
    """Usual floor of rooms, dry soil, lawn, asphalt"""

    HEAVY_PADDING = auto()
    """Excessively thickly upholstered"""

    MATTRESS = auto()
    """Mattress (bed), thick carpet"""

    WET_LEAVES = auto()
    """About 2cm wettish leaves"""

    DRY_LEAVES = auto()
    """About 2cm totally dry leaves"""

    ACCELERATING = auto()
    """Concrete, stony, tiled"""


class IdiomuscularReactionType(Enum):
    """
    Idiomuscular reaction
    Contraction after direct percussion of the muscle (biceps brachii, for example)
    """

    NOT_SPECIFIED = auto()
    """Not specified"""

    ZSAKO = auto()
    """Muscle contraction leading to flexion of the limb"""

    STRONG_REVERSIBLE = auto()
    """Visible contraction band that can be seen with the naked eye"""

    WEAK_PERSISTENT = auto()
    """Discrete, localized contraction that is not visible but palpable"""

    NO_REACTION = auto()
    """No reaction"""


class RigorType(Enum):
    """Rigor type"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    NOT_ESTABLISHED = auto()
    """There is no evidence of rigor mortis having set in"""

    POSSIBLE_REESTABLISHMENT = auto()
    """Early signs of rigor mortis may be present, but it is not fully established"""

    COMPLETE_RIGIDITY = auto()
    """Rigor mortis is fully established, with the body exhibiting maximal stiffness"""

    PERSISTENCE = auto()
    """Rigor mortis persists or may be partially resolved"""

    RESOLUTION = auto()
    """Rigor mortis has fully resolved"""


class LividityType(Enum):
    """Lividity type"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    ABSENT = auto()
    """There is no lividity present"""

    DEVELOPMENT = auto()
    """Lividity is beginning to develop"""

    CONFLUENCE = auto()
    """Lividity is becoming more pronounced and merging"""

    MAXIMUM = auto()
    """Lividity has reached its maximum intensity"""


class LividityDisappearanceType(Enum):
    """Lividity Disappearance type"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    COMPLETE = auto()
    """Lividity disappears totaly at light pressure"""

    INCOMPLETE = auto()
    """Lividity might disappears only with strong pressure (with forceps)"""


class LividityMobilityType(Enum):
    """Lividity Mobility type"""

    NOT_SPECIFIED = auto()
    """Not specified"""

    COMPLETE = auto()
    """Lividity can be completely displaced when the body is turned"""

    PARTIAL = auto()
    """Lividity can be partially displaced when the body is turned"""

    LITTLE_PALOR_ONLY = auto()
    """Lividity shows only a slight change in color (or non change) when the body is turned"""


# --- Constants
# --------------------------------

TEMPERATURE_LIMITS = {
    TemperatureLimitsType.TYMPANIC: (0.0, 37.5),
    TemperatureLimitsType.RECTAL: (0.0, 37.5),
    TemperatureLimitsType.AMBIENT: (-20.0, 37.0)
}
"""Temperature limits in °C ordered by temperature type"""

STANDARD_BODY_TEMPERATURE = 37.2
"""Standard body temperature in °C"""

BODY_MASS_LIMIT = (1.0, 200.0)
"""Body mass limit in Kg"""

CORRECTIVE_FACTOR = {
    BodyCondition.NOT_SPECIFIED: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.0,
        EnvironmentType.MOVING_AIR: 1.0,
        EnvironmentType.WET_STILL_AIR: 1.0,
        EnvironmentType.WET_MOVING_AIR: 1.0,
        EnvironmentType.STILL_WATER: 1.0,
        EnvironmentType.FLOWING_WATER: 1.0,
    },
    BodyCondition.NAKED: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.0,
        EnvironmentType.MOVING_AIR: 0.75,
        EnvironmentType.WET_STILL_AIR: 0.7,
        EnvironmentType.WET_MOVING_AIR: 0.7,
        EnvironmentType.STILL_WATER: 0.5,
        EnvironmentType.FLOWING_WATER: 0.35,
    },
    BodyCondition.LIGHTLY: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.1,
        EnvironmentType.MOVING_AIR: 0.9,
        EnvironmentType.WET_STILL_AIR: 0.8,
        EnvironmentType.WET_MOVING_AIR: 0.7,
        EnvironmentType.STILL_WATER: 0.5,
        EnvironmentType.FLOWING_WATER: 0.35,
    },
    BodyCondition.MODERATELY: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.2,
        EnvironmentType.MOVING_AIR: 1.0,
        EnvironmentType.WET_STILL_AIR: 0.85,
        EnvironmentType.WET_MOVING_AIR: 0.75,
        EnvironmentType.STILL_WATER: 0.6,
        EnvironmentType.FLOWING_WATER: 0.4,
    },
    BodyCondition.WARMLY: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.4,
        EnvironmentType.MOVING_AIR: 1.2,
        EnvironmentType.WET_STILL_AIR: 1.1,
        EnvironmentType.WET_MOVING_AIR: 0.9,
        EnvironmentType.STILL_WATER: 0.7,
        EnvironmentType.FLOWING_WATER: 0.5,
    },
    BodyCondition.HEAVILY: {
        EnvironmentType.NOT_SPECIFIED: 1.0,
        EnvironmentType.STILL_AIR: 1.8,
        EnvironmentType.MOVING_AIR: 1.4,
        EnvironmentType.WET_STILL_AIR: 1.05,
        EnvironmentType.WET_MOVING_AIR: 0.95,
        EnvironmentType.STILL_WATER: 0.75,
        EnvironmentType.FLOWING_WATER: 0.55,
    },
}
"""Corrective factor function of body condition and environment"""

SUPPORTING_BASE_FACTOR = {
    SupportingBase.NOT_SPECIFIED: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 0.0,
        BodyCondition.LIGHTLY: 0.0,
        BodyCondition.MODERATELY: 0.0,
        BodyCondition.WARMLY: 0.0,
        BodyCondition.HEAVILY: 0.0,
    },
    SupportingBase.INDIFFERENT: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 0.0,
        BodyCondition.LIGHTLY: 0.0,
        BodyCondition.MODERATELY: 0.0,
        BodyCondition.WARMLY: 0.0,
        BodyCondition.HEAVILY: 0.0,
    },
    SupportingBase.HEAVY_PADDING: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 1.3,
        BodyCondition.LIGHTLY: 0.3,
        BodyCondition.MODERATELY: 0.2,
        BodyCondition.WARMLY: 0.1,
        BodyCondition.HEAVILY: 0.1,
    },
    SupportingBase.MATTRESS: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 1.1,
        BodyCondition.LIGHTLY: 0.1,
        BodyCondition.MODERATELY: 0.1,
        BodyCondition.WARMLY: 0.1,
        BodyCondition.HEAVILY: 0.1,
    },
    SupportingBase.WET_LEAVES: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 1.3,
        BodyCondition.LIGHTLY: 0.0,
        BodyCondition.MODERATELY: 0.0,
        BodyCondition.WARMLY: 0.0,
        BodyCondition.HEAVILY: 0.0,
    },
    SupportingBase.DRY_LEAVES: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: 1.5,
        BodyCondition.LIGHTLY: 0.0,
        BodyCondition.MODERATELY: 0.0,
        BodyCondition.WARMLY: 0.0,
        BodyCondition.HEAVILY: 0.0,
    },
    SupportingBase.ACCELERATING: {
        BodyCondition.NOT_SPECIFIED: 0.0,
        BodyCondition.NAKED: -0.75,
        BodyCondition.LIGHTLY: -0.2,
        BodyCondition.MODERATELY: -0.2,
        BodyCondition.WARMLY: -0.1,
        BodyCondition.HEAVILY: -0.1,
    },
}
"""Supporting base factor function of supporting base and body condition"""
