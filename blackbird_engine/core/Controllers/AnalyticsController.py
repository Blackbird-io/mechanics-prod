#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.AnalyticsController
"""

Module defines AnalyticsController class.  
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class AnalyticsController    simple Controller that goes through atx until all e done
====================  ==========================================================
"""




#imports
from . import CompletionTests
from .controller import GenericController as Controller
from .Protocol import Protocol




#globals
test_MinComplete = CompletionTests.t_min_quality

#classes
class AnalyticsController(Controller):
    """

    This class manages protocols that provide a focal point for MatchMaker
    analysis. Daughter of Controller class. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a
    
    FUNCTIONS:
    process()
    ====================  ======================================================
    """
    
    def __init__(self):
        Controller.__init__(self)
        
    def process(self,msg):
        Controller.process(self,msg)
        M = self.MR.activeModel
        atx = M.analytics
        #other modules figure out what period M.analytics points towards
        if not getattr(atx,"protocol",None):
            atx.protocol = Protocol()
        if not atx.protocol.pointStandard:
            atx.protocol.pointStandard = test_MinComplete
        newFP = None
        if not atx.protocol.complete:
            test = atx.protocol.pointStandard
            for element in atx.ordered:
                if test(element):
                    continue
                else:
                    newFP = element
                    break
            else:
                atx.protocol.markComplete()
        atx.protocol.focalPoint = newFP
        if newFP:
            M.interview.setFocalPoint(newFP)
        return msg

