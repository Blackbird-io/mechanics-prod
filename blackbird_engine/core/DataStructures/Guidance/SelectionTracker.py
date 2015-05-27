#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.SelectionTracker

"""
This module subclasses Counter into a SelectionTracker object. Instances of
SelectionTracker record topics that are suitable for or selected to work on a
particular object.
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SelectionTracker      specialized gauge to track MatchMaker selections
====================  ==========================================================
"""





#imports
from .Counter import Counter




#globals
#n/a

#classes
class SelectionTracker(Counter):
    """

    Specialized Counter subclass for tracking the MatchMaker's selections for a
    particular object. Relies on Counter attributes to track primary dimension.
    That is, ``self.current`` shows number of times MatchMaker has run a
    topic selection process on the object.

    This counter features a deactivated ``cutOff`` attribute.

    The class includes record-keeping attributes for secondary selection
    metrics, such as ``dryRuns`` (situations where MatchMaker cannot find any
    eligible, unused Topics for the object). Class also provides state for
    MatchMaker caching (``eligibleTopics``,``allScores``).

    NOTE: To reduce memory use, attributes describing topic collections should
    store ONLY TDEXs. Other modules can locate and issue instances of these
    topics from the warehouse as necessary at runtime.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    finishedCatalog       bool, True if no eligible unused Topics in catalog
    eligible              list; bbid cache for topics that can run on obj
    used                  list; bbids for topics that have already processed obj
    
    FUNCTIONS:
    recordDryRun()        toggles instance.finishedCatalog to True
    recordUsedTopic()     adds the topic's TDEX to self.usedTopics
    setEligibles          sets instance.eligibleTopics to passed list of TDEXes
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
            
##    def clear_eligible_topics(self):
##        """
##        STr.clearEligibleTopics() -> None
##        """
##        self.eligibleTopics = []

    def set_eligible(self, known_eligibles):
        self.eligible = known_eligibles
