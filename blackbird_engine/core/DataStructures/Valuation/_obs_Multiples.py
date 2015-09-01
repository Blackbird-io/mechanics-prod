#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.Multiples
"""

Module defines the Multiples class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class Multiples       template w standard fields for multiples
====================  ==========================================================
"""




#imports
from . import Parameters

from .Pattern import Pattern




#globals
#n/a

#classes
class Multiples(Pattern):
    """

    Class provides a dict-like container for tracking multiples. Container
    has standard fields specified in ``fields_multiples`` global in this
    module.

    Each key should point to a dictionary w subfields and numeric values. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def  __init__(self,name = "Multiples",standard = None):
        Pattern.__init__(self,name)
        self.fromkeys(Parameters.fields_multiples)
        self.applyStandard(standard)
