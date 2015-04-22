#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.QualityTracker

"""
This module subclasses Counter into a QualityTracker object
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
QualityTracker        specialized gauge to track quality, includes standards
====================  ==========================================================
"""





#imports
from .Counter import Counter




#globals
#n/a

#classes
class QualityTracker(Counter):
    """
    Specialized Counter for tracking analysis QUALITY for a particular object.
    Relies on Counter attributes to track primary dimension. That is,
    ``self.current`` shows current quality.

    NOTE: Use global variables to scale quality standards.
    A unit of "quality" is supposed to be roughly proportional to a unit of
    "attention."
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    minStandard           quality where item is minimally informative
    maxStandard           quality where item is fully fleshed out and should be
                          left alone in favor of others

    setStandards()        sets minStandard and maxStandard
    ====================  ======================================================
    """
    def __init__(self, minStandard=0, maxStandard=5):
        Counter.__init__(self,cutOff = 10)
        #NOTE: cutoff should probably be a global variable, same w maxStandard
        #and minStandard
        self.setStandards(minStandard,maxStandard)

    def setStandards(self,minStandard=None,maxStandard=None):
        """

        QTr.setStandards([minStandard],[maxStandard]) -> None

        Method sets minStandard, maxStandard for the instance to user-specified
        values or None. 
        """
        self.minStandard = minStandard
        self.maxStandard = maxStandard
