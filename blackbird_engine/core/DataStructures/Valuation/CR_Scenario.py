#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.CR_Scenario
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
from . import Parameters

from .Pattern import Pattern




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
    n/a
    ====================  ======================================================
    """
    
    def __init__(self,name = "CR_Scenario",standard = None):
        Pattern.__init__(self,name)
        self.fromkeys(Parameters.fields_CR_Scenario)
        self.applyStandard(standard)
        #default structure score: 
        self.changeElement("structure", Parameters.gl_structure_score)

