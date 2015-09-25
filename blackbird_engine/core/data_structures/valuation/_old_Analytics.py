#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.Analytics
"""

Module defines the Analytics class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class Analytics       upper-level container for all analytics
====================  ==========================================================
"""




#imports
import copy

from .CreditCapacity import CreditCapacity
from .Pattern import Pattern




#globals
#n/a

#classes
class Analytics(Pattern):
    """

    Class organizes market analytics data about a company.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    activity              dict; views, drills, iois; keyed by timestamp?
    cc                    cc pattern object
    color                 applicable market color
    ev                    ev pattern object
    protocol              placeholder for protocol object
    
    FUNCTIONS:
    copy()                returns a new instance of Pattern
    ====================  ======================================================
    """
    def __init__(self,name="Analytics"):
        Pattern.__init__(self,name)
        cc = CreditCapacity()
        #elements have a specific order:
        self.addElement("cc",cc)
        self.tag("Analytics",field = "req")
        self.tag("ABL")
        self.tag("CC")
        self.tag("EV")
        for e in [self, cc]:   
            e.guide.priority.increment(1)
            e.guide.quality.setStandards(1,3)

    def copy(self):
        """

        Analytics.copy() -> Analytics

        Method returns a new Analytics object. The new object is a deepcopy
        of the instance, with protocol set to None. 
        """
        result = copy.deepcopy(self)
        result.protocol = None
        return result
