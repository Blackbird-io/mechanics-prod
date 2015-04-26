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

from .AttentionTracker import AttentionTracker
from .Counter import Counter
from .QualityTracker import QualityTracker
from .SelectionTracker import SelectionTracker




#globals
#n/a

#classes
class InterviewTracker:
    """

    This class provides state storage for Model-level interview operations, such
    as selecting a path or protocol or developing a structure for the interview.

    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    
    applied_topics              set of topic bbids applied to the Model to date     
    attentionBudget             integer representing total attention resources
    focalPoint                  criterion for MatchMaker's selection
    path                        list of lineitems that act as raw template
    pointStandard               function that tests fp against some internal
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
    setAttentionBudget()        set attentionBudget to new value
    setStructure()              set structure to new object
    setPath()                   set path to a new object
    setProgress()               set progress to higher of current or new,0<=p<=1
    setProtocol()               attach a pointer to a new protocol object
    setFocalPoint()             attach a pointer to the current focal point
    setPointStandard()          attach a decision function for the focal point
    clearCache()                set protocol,structure, activeTest, and fPoint to
                                None
    ==========================  ================================================
    """
    def __init__(self):
        self.applied_topics = set()
        self.attentionBudget = None
        self.focalPoint = None
        self.path = None
        self.pointStandard = None
        self.progress = 0
        self.protocol = None
        self.structure = None
        self.transcript = []
        self.work_space = {}

    def clearCache(self):
        """


        ITr.clearCache() -> None


        """
        self.structure = None
        self.protocol = None
        self.focalPoint = None
        self.pointStandard = None

    def setAttentionBudget(self,aB):
        """


        ITr.setAttentionBudget(aB) -> None


        """
        self.attentionBudget = aB
        
    def setFocalPoint(self,fP):
        """


        ITr.setFocalPoint(fP) -> None


        """
        self.focalPoint = fP

    def setStructure(self,sI):
        """


        ITr.setStructuredInterview(sI) -> None


        """
        self.structure = sI

    def setPath(self,aPath):
        """


        ITr.setPath(aPath) -> None


        Method sets instance.path to the specified object
        """
        self.path = aPath

    def setPointStandard(self,standard):
        """


        ITr.setPointStandard(standard) -> None


        ``standard`` should be a one-argument function that returns a bool
        when applied to an object w a ``guide`` attribute.
        """
        self.pointStandard = standard
        
    def setProgress(self, p, override = False):
        """


        ITr.setProgress(p, override = False) -> None


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
        
    def setProtocol(self,aProl):
        """


        ITr.setProtocol(aProl) -> None

        
        """
        self.protocol = aProl
    
    def transcribe(self,msg):
        """


        ITr.transcribe(msg) -> None


        Appends a tuple of (msg,time of call) to instance.transcript.
        """
        timeStamp = time.time()
        record = (msg,timeStamp)
        self.transcript.append(record)
