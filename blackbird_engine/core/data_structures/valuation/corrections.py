#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.corrections
"""

Module defines Corrections class. Corrections instances record common
adjustments we need to make to user input.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Corrections
====================  ==========================================================
"""




#imports
import BBExceptions
import BBGlobalVariables as Globals




#globals
#n/a

#classes
class Corrections:
    """

    Class stores normalized corrections to user input. Values should be a number
    between 0 and 1.

    For example, suppose you ask Anna how many times a month she goes to the
    zoo. Anna responds, ``10``. You know that people usually exclude petting
    zoos from their calculation; you also know that Anna starts out every day
    by petting her favorite llama Salvador. So under your count, Anna actually
    goes to the zoo 40 times in a month (30 for the daily petting zoo visits,
    10 for the real deal, with rhinos and what not). You would record
    Anna's expected understatement as (40-10)/40, or 0.75.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _overstatement        num; local state, when more is better (user-real)/user
    _understatement       num; local state, when less is better (real-user)/real
    overstatement         num; P, get _overstatement, set for [0, 1)
    understatement        num; P, get _understatement, set for [0, 1)
    
    FUNCTIONS:
    n/a
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    def __init__(self):        
        self._overstatement = Globals.user_correction
        self._understatement = Globals.user_correction

    @property
    def overstatement(self):
        """


        **property**


        Property returns instance._overstatement.

        Property setter accepts values in [0,1). Setter raises
        ManagedAttributeError for values that fall outside of that interval.
        """
        return self._overstatement

    @overstatement.setter
    def overstatement(self, value):
        if 0 <= value < 1:
            self._overstatement = value
        else:
            c = "Adjustment must be a value in [0, 1)."
            raise BBExceptions.ManagedAttributeError(c)

    @property
    def understatement(self):
        """


        **property**


        Property returns instance._understatement.

        Property setter accepts values in [0,1). Setter raises
        ManagedAttributeError for values that fall outside of that interval.
        """
        return self._understatement

    @understatement.setter
    def understatement(self, value):
        if 0 <= value < 1:
            self._understatement = value
        else:
            c = "Adjustment must be a value in [0, 1)."
            raise BBExceptions.ManagedAttributeError(c)
        
