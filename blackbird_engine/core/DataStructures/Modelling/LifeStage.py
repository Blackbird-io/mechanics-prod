#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: LifeStage
"""

Module defines LifeStage class. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LifeStage             objects that provide descriptions of a stage of life

====================  ==========================================================
"""




#imports
from DataStructures.Platform.Tags import Tags
from BBGlobalVariables import *

from .Equalities import Equalities




#globals
#n/a

#classes
class LifeStage(Tags,Equalities):
    """

    Class produces lifeStage objects that fill out a lifeCycle's
    ``allLifeStages`` attribute. Name should be set through self.setName()
    method inherited from Tags class.
    
    Lifestage objects specify temporal values (starts, ends) as percent of
    lifespan completed. 

    NOTE: Drivers or other objects filling out components of larger objects may
    reference current values of life stages. ACCORDINGLY, CARE SHOULD BE TAKEN
    WHEN INTRODUCING NON-DEFAULT LIFESTAGES TO AN OBJECT.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    irrelevantAttributes  ["partOf","parentObject"]
    starts                float or int; lifestage starting point, in percent
    ends                  float or int; lifestage ending point, in percent
    first                 bool; is this stage #1 in list of lifestages
    last                  bool; is this the last stage in list of lifestages
   
    FUNCTIONS:
    makeFirst()           sets stage to first (starts = 0)
    makeLast()            sets stage to last (ends = 100)
    
    ====================  ======================================================

    """
    #define key attributes to simplify comparisons
    keyAttributes = ["starts","ends","name"]
##    irrelevantAttributes = ["allTags","partOf", "parentObject","skipPrefixes"]
    
    def __init__(self, stageName = None, stageStarts = 0, stageEnds = 100):
        Tags.__init__(self)
        Tags.setName(self,stageName)
        self.starts = stageStarts
        self.ends = stageEnds
        self.first = False
        self.last = False
        
    def __str__(self):
        res = ""
        sep = "^"
        width = 10
        if self.first:
            res += sep*width+"\n"
            res += sep*width+"\n"
        else:
            res += sep*width+"\n"
        res += ("NAME:   %s\n" % self.name)
        res += ("starts: %s\n" % self.starts)
        res += ("ends:   %s\n" % self.ends)
        res += ("first:  %s\n" % self.first)
        res += ("last:   %s\n" % self.last)
        if self.last:
            res += sep*width+"\n"
            res += sep*width+"\n"
        else:
            res += sep*width+"\n"
        return res
        
    def makeFirst(self):
        """
        First stage in a allLifeStages list must begin at 0 percentDone.
        """
        self.first = True
        self.starts = 0

    def makeLast(self):
        """
        Last stage in an allLifeStages list must terminate at 100 percentDone.
        A LifeStage object may be both first and last. 
        """
        self.last = True
        self.ends = 100 
