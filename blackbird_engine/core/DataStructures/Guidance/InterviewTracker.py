#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.InterviewTracker

"""
This module defines the InterviewTracker class, which plans and monitors the
interview between Blackbird and a user. 
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
InterviewTracker      plan and monitor machine-user interview
====================  ==========================================================
"""





#imports
import decimal
import time

from Controllers import completion_rules
from DataStructures.Modelling.LineItem import LineItem

from .AttentionTracker import AttentionTracker
from .Counter import Counter
from .QualityTracker import QualityTracker
from .SelectionTracker import SelectionTracker




#globals
intro_line = LineItem("introduction")
intro_line.tag("start",
               "configuration")
intro_line.guide.quality.setStandards(2,5)
quality_rule = completion_rules.check_quality_only

#classes
class InterviewTracker:
    """

    This class provides state storage for Model-level interview operations, such
    as selecting a path or protocol or developing a structure for the interview.

    By default, focal point is a LineItem named "Overview" and standard is the
    min_quality test. 

    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    
    applied_topics              set of topic bbids applied to the Model to date     
    attention_budget            integer representing total attention resources
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    levels                      dict or None; priority groups of items in path
    path                        list of lineitems that act as raw template
    progress                    decimal
    
    transcript                  list of tuples containing message and timestamp
    used                        set of bbids for used topics
    work_space                  unmanaged scrap paper for Topic or other state
    
    FUNCTIONS:
    clear_cache()               clear focal point, rule and levels
    set_attention_budget()      set attentionBudget to new value
    set_completion_rule()       attach a new completion rule to instance
    set_structure()             set structure to new object
    set_path()                  set path to a new object
    set_progress()              set progress to higher of current or new,0<=p<=1
    set_protocol()              attach a pointer to a new protocol object
    set_focal_point()           attach a pointer to the current focal point
    transcribe()                add item to transcript
    ==========================  ================================================
    """
    def __init__(self):
        self.applied_topics = set()
        self.attention_budget = None
        self.completion_rule = quality_rule
        self.focal_point = intro_line.copy()
        self.levels = None
        self.path = None
        self.progress = 0
        self.transcript = []
        self.used = set()
        self.work_space = {}

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

    
    def set_path(self, new_path):
        """


        ITr.set_path(new_path) -> None


        Method sets instance.path to the specified object. Method turns off
        automatic summarization for the new path. 
        """
        self.path = new_path
        if self.path.autoSummarize:
            self.path.autoSummarize = False
        
    def set_progress(self, p, override = False):
        """


        ITr.set_progress(p, override = False) -> None


        Method sets instance progress indicator to the higher of current value
        or ``p`` (progress cannot go down). ``p`` must be between 0 and 100,
        inclusive.

        If ``override`` = True, method sets progress to p for arbitrary p
        values. Use ``override`` = True to reset the indicator to 0. 
        """
        if not override:
            if not 0 <= p <= 100:
                raise BBExceptions.PortalError
            new_p = max(p, self.progress)
        else:
            new_p = p
        new_p = int(new_p)
        self.progress = new_p
        
    def set_protocol(self,aProl):
        """


        ITr.set_protocol(aProl) -> None

        
        """
        self.protocol = aProl
    
    def set_structure(self, new_structure):
        """


        ITr.set_structure(new_structure) -> None


        Method sets instance.structure to argument. 
        """
        self.structure = new_structure

    def transcribe(self,msg):
        """


        ITr.transcribe(msg) -> None


        Appends a tuple of (msg,time of call) to instance.transcript.
        """
        time_stamp = time.time()
        record = (msg,time_stamp)
        self.transcript.append(record)
