#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.interview_tracker

"""
This module defines the InterviewTracker class, a custom stage for managing the
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
from flow import completion_rules
from DataStructures.Modelling.LineItem import LineItem

from .stage import Stage




#globals
intro_line = LineItem("introduction")
intro_line.tag("start",
               "configuration")
intro_line.guide.quality.setStandards(2,5)
quality_rule = completion_rules.check_quality_only

#classes
class InterviewTracker(Stage):
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
    set_progress()              set progress to higher of current or new,0<=p<=1
    ==========================  ================================================
    """
    def __init__(self):
        Stage.__init__(self)
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
                raise BBExceptions.PortalError
            new_p = max(p, self.progress)
        else:
            new_p = p
        new_p = int(new_p)
        self.progress = new_p
        
