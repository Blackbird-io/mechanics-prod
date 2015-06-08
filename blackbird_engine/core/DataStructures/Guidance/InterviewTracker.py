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

from Controllers import CompletionTests
from DataStructures.Modelling.LineItem import LineItem

from .AttentionTracker import AttentionTracker
from .Counter import Counter
from .QualityTracker import QualityTracker
from .SelectionTracker import SelectionTracker




#globals
intro_line = LineItem("introduction")
intro_line.tag("start",
               "configuration",
               "generic")
intro_line.guide.quality.setStandards(2,5)

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
    focal_point                 criterion for MatchMaker's selection
    path                        list of lineitems that act as raw template
    point_standard              function that tests fp against some internal
                                completion standard. function should return
                                ``True`` iff fp satisfies that standard and
                                False otherwise. pointStandard usually set by
                                an external protocol object. May vary over time
                                for any given focalPoint, as protocol cycles
                                through more and more rigorous standards.
    progress                    decimal
    protocol                    generator function that selected current focus
    structure                   dict of priorityLevel items keyed by priority
    transcript                  list of tuples containing message and timestamp
    work_space                  unmanaged scrap paper for Topic or other state
    
    FUNCTIONS:
    transcribe()                add item to transcript
    set_attention_budget()      set attentionBudget to new value
    setStructure()              set structure to new object
    set_path()                   set path to a new object
    setProgress()               set progress to higher of current or new,0<=p<=1
    setProtocol()               attach a pointer to a new protocol object
    setFocalPoint()             attach a pointer to the current focal point
    set_point_standard()          attach a decision function for the focal point
    clear_cache()                set protocol,structure, activeTest, and fPoint to
                                None
    ==========================  ================================================
    """
    def __init__(self):
        self.applied_topics = set()
        self.attention_budget = None
        self.focal_point = intro_line.copy()
        self.path = None
        self.point_standard = CompletionTests.t_min_quality
        self.progress = 0
        self.protocol = None
        self.structure = None
        self.transcript = []
        self.work_space = {}

    def clear_cache(self):
        """


        ITr.clear_cache() -> None


        """
        self.structure = None
        self.protocol = None
        self.focal_point = None
        self.point_standard = None

    def set_attention_budget(self,aB):
        """


        ITr.set_attention_budget(aB) -> None


        """
        self.attention_budget = aB
        
    def set_focal_point(self,fP):
        """


        ITr.set_focal_point(fP) -> None


        """
        self.focal_point = fP

    
    def set_path(self,aPath):
        """


        ITr.set_path(aPath) -> None


        Method sets instance.path to the specified object
        """
        self.path = aPath

    def set_point_standard(self,standard):
        """


        ITr.setPointStandard(standard) -> None


        ``standard`` should be a one-argument function that returns a bool
        when applied to an object w a ``guide`` attribute.
        """
        self.point_standard = standard
        
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


        ITr.setProtocol(aProl) -> None

        
        """
        self.protocol = aProl
    
    def set_structure(self, new_structure):
        self.structure = new_structure

    def transcribe(self,msg):
        """


        ITr.transcribe(msg) -> None


        Appends a tuple of (msg,time of call) to instance.transcript.
        """
        time_stamp = time.time()
        record = (msg,time_stamp)
        self.transcript.append(record)
