#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.YieldCurves
"""

Module defines YieldCruves class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class YieldCurves     container for various yield curves applicable to a name
====================  ==========================================================
"""




#imports
from . import Parameters

from .Pattern import Pattern




#globals
#n/a

#classes
class YieldCurves(Pattern):
    """

    Class provides a dict-like container for tracking yield curves. Container
    has standard fields specified in ``fields_yieldCurves`` global in this
    module.

    Each key should point to a dictionary where values are numeric
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self,name = "YieldCurves",standard = None):
        Pattern.__init__(self,name)
        self.trackChanges = True
        self.fromkeys(Parameters.fields_yieldCurves)
        self.applyStandard(standard)
