# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.guidance.guide

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




# imports
from .attention_tracker import AttentionTracker
from .counter import Counter
from .quality_tracker import QualityTracker
from .selection_tracker import SelectionTracker




# globals
# n/a

# classes
class Guide:
    """

    This class provides an instrumentation cluster for objects that may serve
    as a focal point for MatchMaker.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    HIGHEST_PERMITTED_PRIORITY  int; default of 5

    attention             instance of AttentionTracker
    complete              bool; convenience marker used by external objects
    quality               instance of QualityTracker
    priority              instance of Counter
    selection             instance of SelectionTracker


    FUNCTIONS:
    reset()               resets state attributes of instance
    ====================  ======================================================
    """
    HIGHEST_PERMITTED_PRIORITY = 5

    def __init__(self, priority=None, quality=None):

        self.attention = AttentionTracker()
        self.complete = False

        self.priority = Counter(cut_off=self.HIGHEST_PERMITTED_PRIORITY)

        self.quality = QualityTracker()
        self.selection = SelectionTracker()
        if priority:
            self.priority.current = priority
        if quality:
            self.quality.set_standard(quality)

    def reset(self):
        """
        G.reset() -> None
        """
        Guide.__init__(self)
