#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.Starter

"""
Module responds to a blank starter message (_,_,_) that kicks off every session
with a (M,_,_) message suitable for Analyzer processing. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
MR                    instance of Messenger class, stores last message

FUNCTIONS:
process()             always returns (M,_,_)

CLASSES:
n/a
====================  ==========================================================

"""




#imports
import datetime

import BBGlobalVariables as Globals

from DataStructures.Modelling.Model import Model
from DataStructures.Platform.Messenger import Messenger




#globals
MR = Messenger()

#functions
def process(msg):
    """


    process(msg) -> MQR message


    Function always returns an (M,None,None) message. If the inbound message
    is empty (_,_,_), function creates a new model. Function then starts the
    model and builds out a time line around either the current or globally
    fixed reference date. 
    """
    if Globals.fix_ref_date == True:
        ref_date = Globals.t0
    else:
        ref_date = datetime.date.today()
    MR.clearMessageOut()
    MR.clearMessageIn()
    MR.receive(msg)
    #
    M = msg[0]
    if M:
        model_name = M.portal_data["business_name"]
        if not model_name:
            model_name = Globals.default_model_name
        M.setName(model_name)
        #starter can also do configuration from other parts of
        #user_context
    else:
        M = Model(Globals.default_model_name)
    M.start()
    #
    #make sure to officially ``start`` the model so that it never comes
    #back here; otherwise, all data will be lost
    #
    M.time_line.build(ref_date,
                     Globals.default_periods_fwd,
                     Globals.default_periods_back)
    message = (M, None, None)
    #
    return message
    #
    #SessionController will pass this message to Analyzer, which will use Yenta
    #to select the best intro topic. As is, all models start with the same intro
    #topic, but in the future, the introduction can be customized by geography
    #or business type (based on sign-up code, for example). 
    


