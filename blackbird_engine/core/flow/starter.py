#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: flow.starter

"""
Module defines a starter class for commencing Engine analysis. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Starter               class for starting Engine analysis
====================  ==========================================================
"""




#imports
import datetime

import BBGlobalVariables as Globals

from data_structures.modelling.model import Model
from data_structures.system.messenger import Messenger




#globals
#n/a
    
#classes
class Starter:
    """

    Object prepares a (M, None, None) message at the beginning of an interview
    so that other parts of the Engine can commence work.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    MR                    instance of Messenger

    FUNCTIONS:
    process()             main interace, put togetherg (M, None, None) message
    ====================  ======================================================
    """
        
    def __init__(self):
        self.MR = Messenger()

    def process(self, message):
        """


        Starter.process(message) -> message
        

        Method always returns an (M,None,None) message. Method picks up any
        useful background information that the Portal sends along (e.g.,
        location, type of company associated with access code, etc.).

        If the inbound message is completely empty (_,_,_), method creates a
        new model. Method then starts the model and builds out a time line
        around either the current or globally fixed reference date.
        """
        if Globals.fix_ref_date == True:
            ref_date = Globals.t0
        else:
            ref_date = datetime.date.today()
        #
        self.MR.prep(message)
        #
        model = message[0]
        if model:
            model_name = model.portal_data["business_name"]
            if not model_name:
                model_name = Globals.default_model_name
            model.setName(model_name)
            #starter can also do configuration from other parts of
            #user_context
        else:
            model = Model(Globals.default_model_name)
        model.start()
        #officially ``start`` the model so that it never comes back here;
        #otherwise, starter.process() will destroy all existing model data.
        model.time_line.build(ref_date)
        #
        message = (model, None, None)
        #
        return message
        #
        #SessionController will pass this message to an analyst, which will use Yenta
        #to select the best intro topic. As is, all models start with the same intro
        #topic, but in the future, the introduction can be customized by geography
        #or business type (based on sign-up code, for example). 
        
        
