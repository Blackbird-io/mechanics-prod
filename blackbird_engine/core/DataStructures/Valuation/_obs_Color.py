#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.Color
"""

Module defines the Color class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class Color           container for market color relevant to name
====================  ==========================================================
"""




#imports
from .Multiples import Multiples
from .Pattern import Pattern
from .YieldCurves import YieldCurves




#globals
#n/a

#classes
class Color(Pattern):
    """

    Class that stores aspects of market color applicable to the company at hand.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    comps                 dict of comparable models
    standardMultiples     instance of Multiples showing expected metrics for co
    yieldCurves           instance of YieldCurves (contains numeric values)

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self,name = "Color"):
        Pattern.__init__(self,name)
        comps = {}
        mults = Multiples()
        ycurves = YieldCurves()
        self.addElement("comps",comps)
        self.addElement("standardMultiples",mults)
        self.addElement("yieldCurves",ycurves)
        self.tag("Analytics")
