###############################################################################
# errors n' such
###############################################################################


class OsrsException(Exception):
    def __init__(self, *args):
        self.message = ", ".join(args)

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
