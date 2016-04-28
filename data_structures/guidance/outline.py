#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.outline

"""
This module defines the Outline class, which organizes content, usually in the
form of Step or LineItem objects, into an ordered container that provides the
Engine a roadmap for analysis. 
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Outline               container for organizing steps into a path
====================  ==========================================================
"""




#imports
import time

from .step import Step

from ..modelling.statement import Statement




#globals
#n/a

#classes
class Outline(Step):
    """

    This class provides a foundation for processing roadmaps. Instances start
    out empty, but usually come to include a path of one or more Step objects.

    Instance.protocol_key controls how the interviewer will approach the
    outline. The key must match one of the protocols that the interviewer knows.
    By default, the value is 0, which requires maximum quality analysis for each
    logical step.     
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    attention_budget            integer representing total attention resources
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    levels                      dict or None; priority groups of items in path
    protocol_key                num; which interview protocol should apply 
    track_progress              bool; whether inst supports progress tracking
    work_space                  unmanaged scrap paper for Topic or other state
    
    FUNCTIONS:
     
    clear_cache()               clear focal point, rule and levels
    set_attention_budget()      set attentionBudget to new value
    set_completion_rule()       attach a new completion rule to instance
    set_focal_point()           attach a pointer to the current focal point
    set_path()                  set path to argument or empty Statement 
    ==========================  ================================================
    """
    def __init__(self, name = None):
        Step.__init__(self, name)
        self.attention_budget = None
        self.completion_rule = None
        self.focal_point = None
        self.levels = None
        self.path = None
        self.protocol_key = 0
        self.track_progress = False
        self.work_space = {}

    def clear_cache(self):
        """


        Outline.clear_cache() -> None


        Method clears instance ``completion_rule``, ``focal_point``, and
        ``levels`` attributes.
        """
        self.completion_rule = None
        self.focal_point = None
        self.levels = None

    def set_attention_budget(self,aB):
        """


        Outline.set_attention_budget(aB) -> None


        Method sets instance attention budget.
        """
        self.attention_budget = aB
        

    def set_completion_rule(self, rule):
        """


        Outline.set_completion_rule(rule) -> None


        Method sets instance.completion_rule to argument. Rule should be a
        callable that takes one argument and returns bool (True iff the
        argument is complete).
        """
        self.completion_rule = rule

        
    def set_focal_point(self, fP):
        """


        Outline.set_focal_point(fP) -> None


        Method sets instance.focal_point.
        """
        self.focal_point = fP

    def set_path(self, new_path=None):
        """


        Outline.build_path() -> None


        Method sets instance.path to new_path or an empty Statement.
        Method always sets autoSummarize to False. 
        """
        if new_path:
            self.path = new_path
        else:
            self.path = Statement()
        self.path.autoSummarize = False
        

