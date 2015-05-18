#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Modelling.Stages
"""

Module defines a class that organizes life stage objects.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Stages                organizes life stage objects into a series within [0,100)
====================  ==========================================================
"""




#imports
import BBExceptions



#globals
#n/a

#classes
class Stages:
    """

    Class records and organizes objects that represent various stages of life.
    By definition, life in Blackbird spans from 0 percent complete (inclusive)
    to 100 percent complete (exclusive). Stages must specify an interval that is
    a subset of this main interval.
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    end_points            list; ordered start and end points. stage spans [s,e)
    options               dict; all stage objects, keyed by start point

    FUNCTIONS:
    add_stage()           adds stage to options, runs organize() on instance
    find_stage()          finds a stage that covers specified percent
    organize()            builds end_points from stages in options
    ====================  ======================================================
    """
    def __init__(self):
        self.end_points = []
        self.options = dict()
        
    def add_stage(self, stage):
        """


        Stages.add_stage(stage) -> None


        Method records shallow copy of stage in instance.options under the
        stage's ``starts`` value. Method then organizes the instance. 

        Method expects a dict-type object for ``stage``. Method rasies error
        if start value is outside [0,100).
        """
        stage_start = stage["start"]
        #
        if 0 <= stage_start < 100:
            self.options[stage_start] = stage.copy()
        else:
            c = "Starting point must fall in [0,100)."
            raise BBExceptions.LifeCycleError(c)
        #
        self.organize()
        #

    def find_stage(self, percent):
        """


        Stages.find_stage(percent) -> dict


        Method returns the first stage object in instance.end_points that
        includes the specified percent completion.

        Method returns None if no stage covers the specified percent (usually
        because percent is outside the [0,100) interval).
        """
        result = None
        if not 0<= percent < 100:
            return result
        else:               
            for i in range(1, len(self.end_points)):
                #start at index 1 to make sure loop doesn't run out of length
                stage_starts = self.end_points[i-1]
                stage_ends = self.end_points[i]
                #
                if stage_starts <= percent < stage_ends:
                    result = self.options[stage_starts]
                    break
                else:
                    continue
        #
        return result

    def organize(self):
        """


        Stages.organize() -> None


        Method generates a new instance.end_points list from sorted stage start
        points.
        """
        self.end_points.clear()
        #
        ordered_ends = sorted(self.options.keys())
        self.end_points.extend(ordered_ends)
        #
        self.end_points.append(100)
        
        
        
