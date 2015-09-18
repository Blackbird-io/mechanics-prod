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
from . import completion_rules
from .controller import GenericController as Controller




#globals
#n/a

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
        model = self.MR.activeModel
        atx = model.analytics
        #other modules figure out what period M.analytics points towards
        rule = model.interview.completion_rule
        if not rule:
            rule = completion_rules.check_quality_only
            model.interview.set_completion_rule(rule)
        new_fp = None
        if not atx.guide.complete:
            for element in atx.path:
                if rule(element):
                    continue
                else:
                    new_fp = element
                    break
            else:
                atx.guide.complete = True
        if new_fp:
            model.interview.setFocalPoint(newFP)
        return msg

