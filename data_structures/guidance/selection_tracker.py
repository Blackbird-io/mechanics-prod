#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.selection_tracker

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
from .counter import Counter
from data_structures.system.bbid import ID




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
    reset()               resets state attributes of instance
    set_eligibles         sets eligible to argument
    ====================  ======================================================
    """
    def __init__(self):
        Counter.__init__(self)
        self.finished_catalog = False
        self.eligible = []
        self.used = []

    @classmethod
    def from_database(cls, portal_data):
        new = cls()
        new.__dict__.update(portal_data)
        new.used = [ID.from_database(id).bbid for id in portal_data['used']]

        return new

    def to_database(self):
        data = self.__dict__.copy()
        data['used'] = [id.hex for id in self.used]
        return data

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
