#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.Guide

"""
This module defines the Guide class, which provides a standard gauge cluster for
monitoring how Blackbird analyzes an object.
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Guide                 gauge cluster that guides analysis
====================  ==========================================================
"""





#imports
from .AttentionTracker import AttentionTracker
from .Counter import Counter
from .QualityTracker import QualityTracker
from .SelectionTracker import SelectionTracker




#globals
#n/a

#classes
class Guide:
    """
    This class provides an instrumentation cluster for objects that may serve as
    a focal point for MatchMaker.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    quality               instance of QualityTracker
    attention             instance of AttentionTracker
    selection             instance of SelectionTracker
    priority              instance of Counter

    reset()               reruns __init__ on self
    ====================  ======================================================
    """
    def __init__(self):
        self.quality = QualityTracker()
        self.attention = AttentionTracker()
        self.selection = SelectionTracker()
        self.priority = Counter(cutOff = 5)
        #NOTE: should use global var here for maxPriority

    def reset(self):
        """
        G.reset() -> None
        """
        Guide.__init__(self)
