# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.parameters
"""

Module defines dict-type storage container for parameters.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Parameters            dictionary with overwrite controls
====================  ==========================================================
"""




# Imports
import bb_exceptions




# Constants
# n/a

# Classes
class Parameters(dict):
    """

    Dictionary-type container that monitors whether keys overwrite existing
    data on add() calls.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    add()                 add data, throw exception for overlap with known keys
    copy()                copy the instance and return the copy
    ====================  ======================================================
    """
    def __init__(self):
        dict.__init__(self)

    def add(self, new_data, overwrite=False):
        """


        Parameters.add() -> None


        Add new_data to instance. If overwrite is False, throw [ ] if new_data
        contains keys that already exist in instance. 
        """
        if overwrite:
            self.update(new_data)
        else:
            existing = new_data.keys() & self.keys()
            if existing:
                c = "New params overlap with existing keys. Implicit overwrite prohibited."
                raise bb_exceptions.DefinitionError(existing, c)
            else:
                self.update(new_data)

    def copy(self):
        """


        Parameters.copy() -> obj

        Function returns a copy of the instance.
        """
        dict_copy = dict.copy(self)
        result = Parameters()
        result.update(dict_copy)

        return result
