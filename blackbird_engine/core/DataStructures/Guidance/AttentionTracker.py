#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.QualityTracker

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
from .Counter import Counter




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
    allowance             maximum attention this object can use before it stops
                          being worthwhile to analyze. Set externally.  
    asked                 number of questions asked (to the human user) about
                          this item. 

    setAllowance()        sets allowance
    countAsked()          increments asked by 1 
    clearAsked()          sets asked to 0
    ====================  ======================================================
    """
    def __init__(self):
        Counter.__init__(self,cutOff = 10)
        #NOTE: need global var here for sure
        self.allowance = None
        self.asked = 0

    def setAllowance(self,allowance):
        """

        ATr.setAllowance(allowance) -> None
        """
        self.allowance = allowance

    def countAsked(self):
        """

        ATr.countAsked() -> None
        """
        self.asked +=1
        
    def clearAsked(self):
        """

        ATr.clearAsked() -> None
        """
        self.asked = 0
