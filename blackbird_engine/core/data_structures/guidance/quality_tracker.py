#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.quality_tracker

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
import parameters.guidance

from .counter import Counter




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
    def __init__(self,
                 p_min = parameters.guidance.QUALITY_DEFAULT_MIN_STANDARD,
                 p_max = parameters.guidance.QUALITY_DEFAULT_MAX_STANDARD):
        #
        Counter.__init__(self,
                         cutOff = parameters.guidance.QUALITY_CUT_OFF)
        self.setStandards(p_min, p_max)

    def setStandards(self,minStandard=None,maxStandard=None):
        """

        QTr.setStandards([minStandard],[maxStandard]) -> None

        Method sets minStandard, maxStandard for the instance to user-specified
        values or None. 
        """
        self.standard = minStandard

