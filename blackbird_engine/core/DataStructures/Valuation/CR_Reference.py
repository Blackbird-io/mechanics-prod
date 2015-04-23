#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.CR_Reference
"""

Module defines CR_Reference class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CR_Reference    reference point for a credit outcome w/3 scenarios
====================  ==========================================================
"""




#imports
from . import Parameters

from .CR_Scenario import CR_Scenario
from .Pattern import Pattern




#globals
#n/a

#classes
class CR_Reference(Pattern):
    """

    Class defines a standard credit reference point. Each reference point is
    tied to some fixed value (a 10% wacd or $35mm size). The reference point
    then contains a set of credit scenarios built around this fixed value.

    All reference points contain the core set of scenarios defined through
    ``fields_CR_Reference`` global in this module. Some reference points may
    also contain other data.

    By default, all values in self are instances of CR_Scenario()

    Class accepts a standard scenario that it deepcopies for all values as a
    constructor. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    setAll()
    ====================  ======================================================
    """
    
    def __init__(self, name = "CR_Reference",standard = None):
        Pattern.__init__(self,name)
        self.fromkeys(Parameters.fields_CR_Reference)
        if not standard:
            standard = CR_Scenario()
        self.applyStandard(standard)

    def setAll(self,subKey,val):
        """

        CR_Reference.setAll(subKey,val) -> None

        Method sets the same value for the subKey across all credit scenarios.

        For each scenario in self, method first tries to perform the update via
        Pattern.changeElement(). If that attribute doesn't exist, method falls
        back on regular dictionary value entry.

        If a scenario doesn't have the subKey, method skips it. 
        """
        
        for field in self.keys():
            try:
                try:
                    self[field].changeElement(subKey,val)
                    #first, try the Pattern class method
                except AttributeError:
                    #field is not a Pattern for some reason, try regular dict
                    #method
                    self[field][subKey] = val
            except KeyError:
                continue
