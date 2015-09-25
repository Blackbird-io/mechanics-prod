#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.inflation
"""

Module defines Inflation class to record inflation data in standard format. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Inflation
====================  ==========================================================
"""




#imports
import BBExceptions
import BBGlobalVariables as Globals




#globals
#n/a

#classes
class Inflation:
    """

    Class stores inflation data in a standard format. Property that manages
    ``annual`` attribute limits values to [-1,1] and therefore excludes
    some hyperinflation scenarios. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _annual               num; local state, when more is better (user-real)/user
    annual                num; P, returns _annual, sets in [-1,1]
    
    FUNCTIONS:
    n/a
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    def __init__(self):
        self._annual = Globals.default_inflation

    @property
    def annual(self):
        return self._annual

    @annual.setter
    def annual(self, value):
        if -1 <= value <= 1:
            self._annual = value
        else:
            c = "Annual inflation requires value in [-1,1] interval."
            raise BBExceptions.ManagedAttributeError(c)
