#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: Controllers.SessionController
"""

SessionController delegates message processing to specialized junior modules. 

SessionController sits directly below the Engine Shell. Shell calls
SessionController whenever Shell receives a message (``message A``). SC
processes message A for Shell and returns a different well-formatted MQR
message (``message B``). Shell then passes message B to Portal. Portal combines
message B with user input to form message C. Portal then hands off message C
back to Shell, Shell passes message C to SessionController, and so on.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
MR                    obj; instance of Messenger, stores current message

FUNCTIONS:
check_started()       returns True if message model is started, else False
process()             returns next message from Engine
update_valuation()    

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBExceptions

from DataStructures.Platform.Messenger import Messenger

from . import starter
from ._new_analyst import Analyst



#globals
MR = Messenger()

#functions
def check_started(message):
    """


    check_started(message) -> bool


    Function checks whether Engine has started working on the Model in an MQR
    message. Returns True if message contains a model with M.started == True.
    Function returns False otherwise. 
    """
    result = False
    model = message[0]
    if model:
        if model.started:
            result = True
    return result
    
def process(message):
    """


    process(message) -> message


    Function returns a new MQR message that responds to the input. 

    Function delegates all work to more junior modules. For messages that are
    empty (msg == (None, None, None)) or signal the start of an interview under
    the Engine-Wrapper API, function delegates work to starter. For all other
    messages, function delegates work to analyzer.

    To allow admin to look inside the function-time operation, function stores
    message_in on MR. Function clears MR at the beginning of each call. 
    """
    #Function makes a fresh analyst for every call. This approach helps keep
    #engine completely stateless. The analyst delegates to topics as necessary
    #and then unilaterally determines when the model is done. The analyst
    #returns messages with user-facing questions and a final (M,_,END) with the
    #completed model.
    #
    MR.clearMessageIn()
    MR.clearMQR()
    MR.receive(message)
    #only purpose of MR here is to allow an admin to look inside the engine at
    #run time and see what went in/came out.
    #
    if not check_started(message):
        message = starter.process(message)
    #
    alice = Analyst()
    message = alice.process(message)
    #
    return message

def forecast_terms(model, fixed, ask, ref_date = None):
    """


    forecast_terms(model, fixed, ask[, ref_date = None]) -> (model, ref)


    Function returns a forecast for the terms of a credit transaction on the
    ref_date. If ref_date is None, function returns summary for the existing
    current period.

    Function forecasts outcome on the combined credit surface.

    ``ref_date`` can be datetime.date or ISO-format string object.
    """
    if ref_date:
        model.time_line.update_current(ref_date)
    model = update_valuation(model)
    #
    model.valuation.credit.combine()
    ref = model.valuation.credit.combined.forecast(ask = ask, field = fixed)
    #
    model.time_line.revert_current()
    result = (model, ref)
    #
    return result
    
def summarize_landscape(model, ref_date = None):
    """


    summarize_landscape(model[, ref_date = None]) --> (model, summary)


    Function returns a summary for the combined credit landscape on the
    ref_date. If ref_date is None, function returns summary for the existing
    current period. 

    ``ref_date`` can be datetime.date or ISO-format string object.
    """
    if ref_date:
        model.time_line.update_current(ref_date)
    model = update_valuation(model)
    #
    model.valuation.credit.combine()
    summary = model.valuation.credit.combined.get_summary()
    #
    model.time_line.revert_current()
    result = (model, summary)
    #
    return result

def update_valuation(model):
    """


    proces_analytics(model) -> model
    

    Function gets an analyst to process valuation for the current period.
    """
    model.stage = model.valuation
    #
    message = (model, None, None)
    bella = Analyst()
    message = bella.process(message, run_summary = False)
    #
    updated_model = message[0]
    return updated_model
