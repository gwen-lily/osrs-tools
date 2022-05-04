import numpy as np
from osrs_tools.modifier import Level, Skills
from osrs_tools.stats.stats import PlayerLevels

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-18                                                        #
###############################################################################

###############################################################################
# functions                                                                   #
###############################################################################


def mean_levels(__list: list[PlayerLevels], /) -> PlayerLevels:

    mean_dict: dict[str, Level] = {}

    for skill in Skills:
        lvls = [getattr(lvls, skill.value).value for lvls in __list]
        mean_lvl = Level(int(np.mean(lvls)), "mean party level")
        mean_dict[skill.value] = mean_lvl

    return PlayerLevels(**mean_dict)


###############################################################################
# execution                                                                   #
###############################################################################


def main():

    party_levels: list[PlayerLevels] = []

    for rsn in rsns:
        try:
            party_levels.append(PlayerLevels.from_rsn(rsn))

        except ValueError:
            party_levels.append(PlayerLevels.starting_stats())

    party_mean_levels = mean_levels(party_levels)

    for skill in skills_of_interest:
        val = getattr(party_mean_levels, skill.value)
        _s = f"skill: {skill.name}, avg lvl: {val}"
        print(_s)


if __name__ == "__main__":

    rsns = [
        "centihybrid",
        "decihybrid",
        "GoldKINK11",
        "KawaBonga",
        "KawaBonk",
        "KawaDonatelo",
        "KawaLeonardo",
        "KawaMikey",
        "KawaRaphael",
        "KawaScout",
        "KawaSplinter",
        "marlunar99",
        "microhybrid",
        "millihybrid",
        "nanohybrid",
        "picohybrid",
        "sirbedevere",
        "sirbussy",
        "sirelectra",
        "sirnargeth",
        "sirpalamedes",
        "sirpolymnia",
        "wiki aragorn",
        "wiki bilbo",
        "wiki boromir",
        "wiki gimli",
        "wiki legolas",
    ]

    skills_of_interest = [
        Skills.THIEVING,
    ]

    main()
