#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.attention_tracker
"""
This module subclasses Counter into a AttentionTracker object
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
AttentionTracker      specialized gauge to track attention, includes allowance
====================  ==========================================================
"""




#imports
from .counter import Counter




#globals
#n/a

#classes
class AttentionTracker(Counter):
    """

    Specialized Counter subclass for tracking ATTENTION COST for the analysis of
    a particular object. Relies on Counter attributes to track primary
    dimension. That is, ``self.current`` shows attention expended to date.

    Includes record-keeping attributes (``allowance``, ``questionsAsked``) that
    permit higher-level objects to allocate resources. 
    
    NOTE: Use global variables to scale quality standards.
    A unit of "quality" is supposed to be roughly proportional to a unit of
    "attention."
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    allowance             maximum attention this object can use before it stops
                          being worthwhile to analyze. Set externally.  
    asked                 number of questions asked (to the human user) about
                          this item.
    ATTENTION_MAX         maximum size for attention budget

    FUNCTIONS:
    clear_asked()         sets asked to 0
    count_asked()         increments asked by 1
    reset()               resets state attributes of instance
    set_allowance()       sets allowance
    ====================  ======================================================
    """
    ATTENTION_MAX = 10
    
    def __init__(self):
        Counter.__init__(self, cut_off=self.ATTENTION_MAX)
        self.allowance = None
        self.asked = 0

    @classmethod
    def from_database(cls, portal_data):
        new = cls()
        new.__dict__.update(portal_data)
        return new

    def to_database(self):
        data = self.__dict__
        return data

    def clear_asked(self):
        """

        ATr.clear_asked() -> None
        """
        self.asked = 0

    def count_asked(self):
        """

        ATr.count_asked() -> None
        """
        self.asked +=1

    def set_allowance(self,allowance):
        """

        ATr.set_allowance(allowance) -> None
        """
        self.allowance = allowance
