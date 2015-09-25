#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.guide

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
from .attention_tracker import AttentionTracker
from .counter import Counter
from .quality_tracker import QualityTracker
from .selection_tracker import SelectionTracker




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

    DATA:
    attention             instance of AttentionTracker
    complete              bool; convenience marker used by external objects
    quality               instance of QualityTracker
    priority              instance of Counter
    selection             instance of SelectionTracker
    
    FUNCTIONS:
    reset()               reruns __init__ on self
    ====================  ======================================================
    """
    def __init__(self):
        self.attention = AttentionTracker()
        self.complete = False
        self.priority = Counter(cutOff = 5)
        self.quality = QualityTracker()
        self.selection = SelectionTracker()
        #NOTE: should use global var here for maxPriority

    def reset(self):
        """
        G.reset() -> None
        """
        Guide.__init__(self)
