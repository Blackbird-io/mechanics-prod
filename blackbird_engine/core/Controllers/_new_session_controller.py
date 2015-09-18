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
process_analytics()   returns model with market analytics data

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

#classes
#n/a

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
    #
    if not check_started(message):
        message = starter.process(message)
    #
    alice = Analyst()
    message = alice.process(message)
    #
    return message

def update_valuation(model, ref_date = None):
    """


    proces_analytics(model[, ref_date = None]) -> model
    

    Function gets an analyst to process valuation for the model, as of the
    ref_date. If ref_date is None, function processes valuation for the current
    period. If ``revert`` is True, function reverts the model to the original
    period before returning it.

    ``ref_date`` can be datetime.date or ISO-format string object.
    """
    old_ref_date = model.time_line.current_period.start
    if ref_date:
        model.time_line.update_current(ref_date)
    #
    model.stage = model.valuation
    message = (model, None, None)
    #set direction for analyst: model.valuation always points to current period
    #valuation. 
    #
    bella = Analyst()
    message = bella.process(message, run_summary = False)
    #skip summary for speed
    del model
    updated_model = message[0]
    #
    if revert:
        updated_model.time_line.update_current(old_ref_date)
    #
    return updated_model
    #
    #

#Shell deals with Portal- and API- format objects, conforms things to Schema, etc,
#but doesnt do substantive processing work. that goes to layers below. 

def get_landscape_summary(model, ref_date = None, revert = True):
    """
    --> (model, summary)
    """
    result = None
    #
    #allow for reversion **here**
    old_ref_date = model.time_line.current_period.start #should this be the end date? check what falls into period
    if ref_date:
        model.time_line.update_current(ref_date)
    model = update_valuation(model) #<-----------------------------------runs only on current period, always; 
    summary = model.valuation.cc.landscape.getSummary()
    #
    if revert:
        model.time_line.update_current(old_ref_date)
    #
    result = [model, summary]
    #
    return result
    #shell will then convert the model back into portal_model, make sure summary
    #fits the schema, and call it a day

#may be these methods should always revert?
def get_forecast(model, x_axis, x_value, ref_date = None, revert = True):
    result = None
    #
    old_ref_date = model.time_line.current_period.blah
    if ref_date:
        model.time_line.update_current(ref_date)
    model = update_valuation(model)
    ref = model.valuation.cc.landscape.forecast(ask = ask, field = fixed)
    #
    if revert:
        model.time_line.update_current(old_ref_date)
    return [model, ref]
    
    
