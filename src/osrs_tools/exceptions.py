"""The basic exception for the osrs-tools module.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

###############################################################################
# main class                                                                  #
###############################################################################


class OsrsException(Exception):
    def __init__(self, *args):
        self.message = ", ".join([str(a) for a in args])

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
