#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.SelectionTracker

"""
Module subclasses Counter into a SelectionTracker object.
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SelectionTracker      specialized gauge to track topic selections
====================  ==========================================================
"""




#imports
from .Counter import Counter




#globals
#n/a

#classes
class SelectionTracker(Counter):
    """

    The SelectionTracker provides a Counter subclass specialized for tracking
    topics selected for a particular object. The SelectionTracker relies on
    Counter attributes (.current) to count attempts and other attributes.

    NOTE: Sets of topics should store only bbids for those topics.
    Storing pointers to actual topic objects can break serialization and deep
    copying. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    finished_catalog      bool; True if all eligible topics in catalog used
    eligible              list; bbid cache for topics that can run on obj
    used                  list; bbids for topics that have already processed obj
    
    FUNCTIONS:
    record_dry_run()      sets finished_catalog to True
    record_used_topic()   adds topic bbid to used list
    set_eligibles         sets eligible to argument
    ====================  ======================================================
    """
    def __init__(self):
        Counter.__init__(self)
        self.finished_catalog = False
        self.eligible = []
        self.used = []
    
    def record_dry_run(self):
        """


        ST.record_dry_run() -> None


        Sets instance.finished_catalog to True
        """
        self.finished_catalog = True

    def record_used_topic(self,T):
        """


        ST.record_used_topic(T) -> None


        Method appends topic bbid to instance.used list.
        """
        self.used.append(T.id.bbid)
            
    def set_eligible(self, known_eligibles):
        """


        ST.set_eligible(known_eligibles) -> None


        Method sets instance.eligible to argument
        """
        self.eligible = known_eligibles
