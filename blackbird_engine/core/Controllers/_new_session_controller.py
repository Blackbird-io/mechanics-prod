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
from .analyst import Analyst



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
    #Function makes a fresh analyst for every call to keep processing completely
    #stateless for each model. The analyst delegates to topics as necessary.
    #when the analyst determines that the model is done, they tell client
    #modules higher up to conclude the interview by passing a (M,_,END) message.
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

def process_analytics(model, ref_date = None):
    """


    proces_analytics(model[, ref_date = None]) -> model
    

    Function locates the time period that includes the ``ref_date``, gets an
    analyst to process the company valuation for that time period, and returns
    a model where model.valaution points at the ref_period's valuation. 

    ``ref_date`` can be datetime.date or ISO-format string object.
    """
    if ref_date:
        model.time_line.update_current(ref_date)
    company_snapshot = model.time_line.current_period.content
    #
    model.valuation = company_snapshot.valuation
    model.stage = model.valuation
    #
    message = (model, None, None)
    #
    bella = Analyst()
    message = bella.process(message, run_summary = False)
    #think about whether you want to update summary here. theoretically, the
    #summary should stay the same; or may be want to remove the summary altogether?
    #or put it on the business unit. which seems like it makes most sense. 
    updated_model = message[0]
    #
    return updated_model
    
