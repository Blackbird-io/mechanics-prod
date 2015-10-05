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

    A unit of "quality" is supposed to be roughly proportional to a unit of
    "attention."    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    standard              quality score where item is considered ``done``

    FUNCTIONS:
    set_standard()        sets standard
    ====================  ======================================================
    """
    def __init__(self, standard = parameters.guidance.QUALITY_DEFAULT):
        #
        Counter.__init__(self, cut_off = parameters.guidance.QUALITY_MAX)
        self.set_standard(standard)

    def set_standard(self, standard):
        """


        QTr.set_standard(standard) -> None


        Method sets minStandard, maxStandard for the instance to user-specified
        values or None. 
        """
        self.standard = standard

