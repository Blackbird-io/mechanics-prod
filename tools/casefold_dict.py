# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: tools.casefold_dict
"""

Miscellaneous printing routines. All format objects into strings or lists of
strings.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
CasefoldDict          dictionary for case-insensitive lookup
====================  ==========================================================
"""




# Imports
# n/a




# Globals
# n/a


# Definitions
class CasefoldDict(dict):
    """

    A dict that stores and looks up values by the lower case key.
    """

    def __keytransform__(self, key):
        """

        CasefoldDict.__keytransform__() -> obj
        """

        if isinstance(key, (str, bytes)):
            key = key.casefold()
        return key

    def __getitem__(self, key):
        """

        CasefoldDict.__getitem__() -> obj
        """

        return dict.__getitem__(self, self.__keytransform__(key))

    def __setitem__(self, key, value):
        """

        CasefoldDict.__setitem__() -> None
        """

        return dict.__setitem__(self, self.__keytransform__(key), value)

    def __delitem__(self, key):
        """

        CasefoldDict.__delitem__() -> None
        """

        return dict.__delitem__(self, self.__keytransform__(key))

    def __contains__(self, key):
        """

        CasefoldDict.__contains__() -> Bool
        """

        return dict.__contains__(self, self.__keytransform__(key))
