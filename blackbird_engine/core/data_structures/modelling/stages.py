#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.stages
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
    by_name               dict; all stage objects, keyed by name, SSOT
    by_start              dict; all stage objects, by start, from by_name data
    end_points            list; ordered start and end points. stage spans [s,e)
    

    FUNCTIONS:
    add_stage()           adds stage to by_name, runs organize() on instance
    copy()                return new instance with shallow copies of attrs
    find_stage()          finds a stage that covers specified percent
    organize()            builds end_points from stages in by_name
    ====================  ======================================================
    """
    def __init__(self):
        self.by_name = dict()
        self.by_start = dict()
        self.end_points = []
        
    def add_stage(self, stage):
        """


        Stages.add_stage(stage) -> None


        Method records a **shallow copy** of stage in instance.by_name under the
        stage's ``name`` value and in by_start under the stage's start value.

        Method organizes the instance at every call.

        Method expects a dict-type object for ``stage``. Method rasies error
        if stage start value is outside [0,100). To maintain deterministic
        outcomes on find_stage(), method also raises error if instance already
        contains a stage that starts at the same percent as the argument. 
        """
        stage_start = stage["start"]
        stage_name = stage["name"]
        #
        if 0 <= stage_start < 100:
            if stage_start not in self.by_start:
                clean_stage = stage.copy()
                self.by_name[stage_name] = clean_stage
                self.by_start[stage_start] = clean_stage
            else:
                c = "Instance already contains stage that starts at %s percent."
                c = c % stage_start
                raise BBExceptions.LifeCycleError(c)
        else:
            c = "Starting point must fall in [0,100)."
            raise BBExceptions.LifeCycleError(c)
        #
        self.organize()

    def copy(self):
        """


        Stages.copy() -> Stages


        Method returns a new instance of Stages. Result attributes are shallow
        copies of seed attributes. 
        """
        result = Stages()
        result.by_name = self.by_name.copy()
        result.by_start = self.by_start.copy()
        result.end_points = self.end_points[:]
        #
        return result
        
    def find_stage(self, percent):
        """


        Stages.find_stage(percent) -> dict


        Method returns the first stage object in instance.end_points that
        includes the specified percent completion.

        Method returns None if no stage covers the specified percent (usually
        because percent is outside the [0,100) interval).
        """
        result = None
        if percent is None:
            return result
            #to avoid sorting errors
        if not 0<= percent < 100:
            return result
        else:               
            for i in range(1, len(self.end_points)):
                #start at index 1 to make sure loop doesn't run out of length
                stage_starts = self.end_points[i-1]
                stage_ends = self.end_points[i]
                #
                if stage_starts <= percent < stage_ends:
                    result = self.by_start[stage_starts].copy()
                    result["end"] = stage_ends
                    #add some info to the stage before returning it
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

        On every call, method clears and then rebuilds instance.by_start from
        data in instance.by_name.
        """
        self.by_start.clear()
        self.end_points.clear()
        #
        for stage in self.by_name.values():
            stage_start = stage["start"]
            self.by_start[stage_start] = stage
        #
        ordered_ends = sorted(self.by_start.keys())
        self.end_points.extend(ordered_ends)
        #
        self.end_points.append(100)        
