#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.guidance.interview_tracker

"""
This module defines the InterviewTracker class, a custom Outline for managing
the interview between Blackbird and a user. 
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
import copy
import bb_exceptions

from flow import completion_rules

from data_structures.modelling.line_item import LineItem
from data_structures.modelling.link import Link

from .outline import Outline




#globals
intro_line = LineItem("introduction")
intro_line.tag("start",
               "configuration")
intro_line.guide.quality.set_standard(2)
quality_rule = completion_rules.check_quality_only

#classes
class InterviewTracker(Outline):
    """

    This class provides a ready-to-go container for managing how Blackbird
    interviews a user. Includes a default focal point and completion standard.

    The default protocol key for instances is set to 1 to require interviewer
    to balance quality with priority.
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    protocol_key                set to 1 by default
    progress                    num; starts at 0
    track_progress              True
    
    FUNCTIONS:
    copy()                      return copy of the instance with state reset
    set_progress()              set progress to higher of current or new,0<=p<=1
    ==========================  ================================================
    """
    def __init__(self):
        Outline.__init__(self, "interview")
        self.completion_rule = quality_rule
        self.focal_point = intro_line.copy()
        self.progress = 0
        self.protocol_key = 1
        self.track_progress = True
        
    def set_progress(self, p, override = False):
        """


        InterviewTracker.set_progress(p, override = False) -> None


        Method sets instance progress indicator to the higher of current value
        or ``p`` (progress cannot go down). ``p`` must be between 0 and 100,
        inclusive.

        If ``override`` = True, method sets progress to p for arbitrary p
        values. Use ``override`` = True to reset the indicator to 0. 
        """
        if not override:
            if not 0 <= p <= 100:
                raise bb_exceptions.PortalError
            new_p = max(p, self.progress)
        else:
            new_p = p
        new_p = int(new_p)
        self.progress = new_p

    def copy(self):
        """


        InterviewTracker.copy() -> InterviewTracker


        Method makes a copy of the instance, preserving the path, priority
        level, quality standard, available attention, and selection cut-off of
        itself and all items along its path. Links in path are set to None.

        Current status of all counters is reset to zero. Focal point is set to
        None.
        """
        result = copy.deepcopy(self)

        result.progress = 0
        result.focal_point = None

        result.guide.reset()

        if result.path:
            for step in result.path.get_full_ordered():
                step.guide.reset()

                # don't allow implicit copy of Link objects, break Link by
                # setting Link.target = None
                if isinstance(step, Link):
                    step.target = None

        return result
