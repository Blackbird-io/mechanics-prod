#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: Controllers.SessionController
"""

SessionController delegates message prociessing to specialized junior modules. 

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
process_summary()     returns model with summary

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBExceptions

from DataStructures.Platform.Messenger import Messenger

from . import Analyzer
from . import Starter




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
    M = message[0]
    if M:
        if M.started:
            result = True
    return result
    
def process(message_in):
    """


    process(message_in) -> message


    Function returns a new MQR message that responds to the input. 

    Function delegates all work to more junior modules. For messages that are
    empty (msg == (None, None, None)) or signal the start of an interview under
    the Engine-Wrapper API, function delegates work to Starter. For all other
    messages, function delegates work to Analyzer.

    To allow admin to look inside the function-time operation, function stores
    message_in on MR. Function clears MR at the beginning of each call. 
    """
    #
    #store message on Messenger instance while processing below. Admin can then
    #look inside the function-time process chain
    MR.clearMessageIn()
    MR.clearMQR()
    MR.receive(message_in)
    #
    #check if message is well formed
    if len(message_in) != 3:
        c = "Engine message violates length-3 expectation."
        raise BBExceptions.PortalError(c)
    #
    if not check_started(message_in):
        message_mid = Starter.process(message_in)
        message_out = Analyzer.process(message_mid)
    else:
        message_out = Analyzer.process(message_in)
        #
        #Analyzer will determine when it's time to conclude the interview. At
        #that time, Analyzer will return a M_End message. In continuous
        #operation, Shell will terminate the collection-analysis loop when it
        #receives this type of message. Web Portal reacts the same way.
    #
    return message_out
    #

def process_analytics(starting_model):
    """


    process_analytics(engine_model) -> Model

    
    Function returns the starting model with market analytics data. 
    
    Function packages the starting model into a (M,_,_) message. Function then
    passes the message down to Analyzer.process_analytics() for actual work.

    NOTE: The output model should generally have the same memory address as the
    input model, but function does not guarantee shared or different identity. 
    """
    msg = (starting_model, None, None)
    msg = Analyzer.process_analytics(msg)
    updated_model = msg[0]
    return updated_model

def process_summary(starting_model):
    """


    process_summary(starting_model) -> Model

    
    Function returns the starting model with a summary.
    
    Function packages the starting model into a (M,_,_) message. Function then
    passes the message down to Analyzer.process_summary() for actual work.

    NOTE: The output model should generally have the same memory address as the
    input model, but function does not guarantee shared or different identity. 
    """
    msg = (starting_model, None, None)
    msg = Analyzer.process_summary(msg)
    updated_model = msg[0]
    return updated_model
    
