#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.stage

"""
This module defines the Stage class, which organizes content into a path for
processing. 
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Stage                 container for organizing steps into a path
====================  ==========================================================
"""





#imports
import time

from .step import Step




#globals
#n/a

#classes
class Stage(Step):
    """

    This class provides a foundation for processing roadmaps. Instances start
    out empty, but usually come to include a path of one or more Step objects. 
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    attention_budget            integer representing total attention resources
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    levels                      dict or None; priority groups of items in path
    track_progress              bool; whether stage supports progress tracking
    work_space                  unmanaged scrap paper for Topic or other state
    
    FUNCTIONS:
    build_path()                set path to an empty Financials instance 
    clear_cache()               clear focal point, rule and levels
    set_attention_budget()      set attentionBudget to new value
    set_completion_rule()       attach a new completion rule to instance
    set_focal_point()           attach a pointer to the current focal point
    ==========================  ================================================
    """
    def __init__(self, name = None):
        Step.__init__(self, name)
        self.attention_budget = None
        self.completion_rule = None
        self.focal_point = None
        self.levels = None
        self.path = None
        self.track_progress = False
        self.work_space = {}

    def build_path(self):
        """


        WorkStage.build_path() -> None


        Method sets instance.path to an empty Financials object. 
        """
        self.path = Financials(populate = False)
        self.path.autoSummarize = False

    def clear_cache(self):
        """


        ITr.clear_cache() -> None


        Method clears instance ``completion_rule``, ``focal_point``, and
        ``levels`` attributes.
        """
        self.completion_rule = None
        self.focal_point = None
        self.levels = None

    def set_attention_budget(self,aB):
        """


        ITr.set_attention_budget(aB) -> None


        """
        self.attention_budget = aB
        

    def set_completion_rule(self, rule):
        """


        ITr.set_completion_rule(rule) -> None


        Method sets instance.completion_rule to argument. Rule should be a
        callable that takes one argument and returns bool (True iff the
        argument is complete).
        """
        self.completion_rule = rule

        
    def set_focal_point(self,fP):
        """


        ITr.set_focal_point(fP) -> None


        """
        self.focal_point = fP
