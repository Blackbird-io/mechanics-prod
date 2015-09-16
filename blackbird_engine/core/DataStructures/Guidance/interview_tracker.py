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
from Controllers import completion_rules
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

    This class provides state storage for Model-level interview operations, such
    as selecting a path or protocol or developing a structure for the interview.

    By default, focal point is a LineItem named "Overview" and standard is the
    min_quality test. 

    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    progress                    num; starts at 0
    
    FUNCTIONS:
    set_progress()              set progress to higher of current or new,0<=p<=1
    ==========================  ================================================
    """
    def __init__(self):
        Stage.__init__(self)
        self.completion_rule = quality_rule
        self.focal_point = intro_line.copy()
        self.progress = 0
        
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
        
