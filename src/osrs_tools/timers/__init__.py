"""The timers and tickers sub-module of osrs-tools.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-02                                                        #
###############################################################################
"""


from .tickers import CharacterUpdater, PlayerUpdater
from .timers import (
    GET_UPDATE_CALLABLE,
    Effect,
    RepeatedEffect,
    TimedEffect,
    TimedEffectExpired,
    Timer,
    TimerExpired,
)
