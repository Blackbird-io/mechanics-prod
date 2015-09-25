#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.cr_scenario
"""

Module that subclasses Pattern into CR_Scenario, which summarizes the most
important characteristics of a credit transaction. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CR_Scenario     template for summarizing a credit transaction
====================  ==========================================================
"""




#imports
from . import parameters

from .pattern import Pattern




#globals
#n/a

#classes
class CR_Scenario(Pattern):
    """

    Class defines a set of fields that summarizes the most important
    characteristics of a credit transaction. Fields come from
    ``fields_CR_Scenario`` global defined in this module. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    to_portal()           Return a dictionary with instance contents
    ====================  ======================================================
    """
    
    def __init__(self,name = "CR_Scenario",standard = None):
        Pattern.__init__(self,name)
        self.fromkeys(parameters.fields_CR_Scenario)
        self.applyStandard(standard)
        #default structure score: 
        self.changeElement("structure", parameters.gl_structure_score)

    def to_portal(self, seed = None):
        """


        CR_Scenario.to_portal([seed = None]) -> dict()


        Method updates an empty dictionary with data from seed. If ``seed`` is
        None, method uses instance as seed.
        """
        if not seed:
            seed = self
        result = dict()
        result.update(seed)
        return result

