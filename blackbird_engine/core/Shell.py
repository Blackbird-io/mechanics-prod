#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Shell
"""

Module provides a shell that supports the main Engine services. Shell enforces
schemas and acts as a type adapter between the inside and outside of the Engine.
Shell generally avoids looking ``inside`` the Engine model. Instead, it prefers
to delegate all such substantive work to lower-level components.

SimplePortal to provide a command-line user interface.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
launched              bool; True if Shell has served up a message, else False
MR                    obj; instance of Messenger
script                obj; dictionary of pre-set responses
show_responses        bool; whether WebPortal should display scripted responses
trace                 bool; whether Engine should trace analysis
web_mode              bool; if True, Shell returns fully flattened objects

FUNCTIONS:
continuous()          function runs analysis continuously until completion
disable_script()      removes script reference
disable_web_mode()    turns off web mode, permits rich InputElement objects
enable_web_mode()     turns on web mode, requires API-compliant delivery
get_forecast()        computes terms for a transaction on the model
get_landscape_summary describes the opportunity landscape for all transactions 
next_question()       uses SimplePortal to ask for the next user input
step()                performs one analytical step, from User to Engine to User
to_portal()           converts MQR message to Engine-Wrapper API dict format
to_engine()           converts API message to MQR
use_script()          commits SimplePortal to get user responses from a script

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import sys
import os

c = "CWD: \n%s\n" % os.getcwd()
print(c)
c = "Python Path (via sys): \n%s\n" % sys.path
print(c)
sub_folder = r"blackbird_engine/core"
sub_folder = os.path.normpath(sub_folder)
if sub_folder not in sys.path:
    sys.path.append(sub_folder)

import simple_portal as Portal
import BBGlobalVariables as Globals

from content import question_manager as QuestionManager
from data_structures.modelling.model import Model as EngineModel
from data_structures.portal.portal_model import PortalModel
from data_structures.system.messenger import Messenger
from data_structures.valuation.cr_reference import CR_Reference
from flow import supervisor




#globals
blank_credit_reference = CR_Reference()
launched = False
low_error = False
MR = Messenger()
pm_converter = PortalModel()
script = None
show_responses = False
trace = False
web_mode = True

QuestionManager.populate()
#QM.populate() should run a no-op here because downstram modules beat Shell to
#the punch

#functions
def continuous(first_message = None, cycles = 200, portal_format = False):
    """


    Shell.continuous([first_message = None
                     [, cycles = 200
                     [, portal_format = False]]]) -> obj


    Function runs a continuous processing loop until Engine completes the
    interview or the number of iterations exceeds the ``cycles``
    circuit-breaker, whichever is earlier. Function then returns the last
    message.

    Cycles count the number of moves between Shell and Engine, so each question
    or answer takes up one cycle. To get a model after 6 scripted answers, run
    the function for 12 cycles.

    Function will start work from the first_message, if one is specified. The
    first message **must** be in PortalMessage format. Without a first message,
    function will start with the launch message from Simple Portal. 

    If ``portal_format`` is True, function returns a message that complies with
    the API spec for PortalMessage. Otherwise, function returns an MQR message.
    """
    last_message = None
    #
    MR.clearMessageIn()
    MR.clearMessageOut()
    MR.clearMQR()
    #
    if not first_message:
        #launch the Portal and get the first message from the Engine before
        #moving to loop
        MR.messageOut = Portal.launch("iop start")
        message_for_engine = to_engine(MR.messageOut)
        MR.messageIn = supervisor.process(message_for_engine)
        MR.messageOut = None
        #
        last_message = MR.messageIn
        if portal_format:
            last_message = to_portal(last_message)
        #
    else:
        #caller specified a starting message
        M = first_message["M"]
        Q = first_message["Q"]
        R = first_message["R"]
        mock_engine_msg = (M,Q,R)
        #skip expensive formal unpack for now
        status = Globals.checkMessageStatus(mock_engine_msg)
        if status == Globals.status_pendingQuestion:
            MR.messageIn = to_engine(first_message)
            #convert message so it tracks standard supervisor output; that way,
            #can use loop to keep track of cycles without running ``shadow``
            #processing beforehand
            #
        else:
            MR.messageOut = first_message
        #
        if portal_format:
            last_message = first_message
        else:
            last_message = to_engine(first_message)
        #
    #
    #now start looping
    n = 0
    while n < cycles:
        #to make sure portal sees MQEND, break only when checking message out
        if MR.messageOut:
            message_for_engine = to_engine(MR.messageOut)
            status = Globals.checkMessageStatus(message_for_engine)
            if status == Globals.status_endSession:
                last_message = message_for_engine
                if portal_format:
                    last_message = MR.messageOut
                break
            else:
                MR.messageIn = supervisor.process(message_for_engine)
                MR.messageOut = None
        elif MR.messageIn:
            status = Globals.checkMessageStatus(MR.messageIn)
            message_for_portal = to_portal(MR.messageIn)
            MR.messageOut = Portal.process(message_for_portal,
                                           display = show_responses)
            MR.messageIn = None
        n = n + 1
    #
    return last_message

def disable_script():
    """


    disable_script() -> None


    Function turns off script mode by passing None to use_script().
    """
    use_script(None)

def disable_web_mode():
    """


    disable_web_mode() -> None


    Function sets turns off web mode: sets module global ``web_mode`` to False.
    
    In web mode, Shell will format outbound (Portal-facing) messages with fully
    ``flat`` Q objects, where every attribute value is a built-in, JSON
    compatible object, per the Engine-Wrapper API. In particular, in web mode,
    question["input_array"] is a list of plain dictionaries that comply with the
    API InputElement schema. 

    If web mode is off, Shell will permit outbound messages to contain ``rich``
    objects in the question input array. In particular, when web_mode == False,
    question[``input_array``] will be a list of instances of type-specific
    subclasses of Platform.Analysis.InputElements.GenericInput. These objects
    provide response verification and pretty printing logic on top of standard
    API data. 
    """
    global web_mode
    web_mode = False
    Portal.disable_web_mode()

def enable_web_mode():
    """


    enable_web_mode() -> None


    Function sets turns on web mode: sets module global ``web_mode`` to True.
    
    In web mode, Shell will format outbound (Portal-facing) messages with fully
    ``flat`` Q objects, where every attribute value is a built-in, JSON
    compatible object, per the Engine-Wrapper API. In particular, in web mode,
    question["input_array"] is a list of plain dictionaries that comply with the
    API InputElement schema. 

    If web mode is off, Shell will permit outbound messages to contain ``rich``
    objects in the question input array. In particular, when web_mode == False,
    question[``input_array``] will be a list of instances of type-specific
    subclasses of Platform.Analysis.InputElements.GenericInput. These objects
    provide response verification and pretty printing logic on top of standard
    API data.
    """
    global web_mode
    web_mode = True
    Portal.enable_web_mode()

def get_forecast(portal_model, fixed, ask, ref_date = None):
    """
    

    get_forecast(portal_model, fixed, ask) -> [PortalModel,
                                               fixed,
                                               ask,
                                               CreditReference]


    **API SPEC**

    Function returns a CreditReference that outlines bad, mid, and good
    CreditScenarios.
    """
    #convert portal_model to engine format, then send down to supervisor for
    #substantive analysis.
    engine_model = EngineModel.from_portal(portal_model)
    engine_model, ref = supervisor.forecast_terms(engine_model,
                                                  fixed,
                                                  ask,
                                                  ref_date)
    #ref comes back as a CR_Reference object. Flatten for output.
    new_model = pm_converter.to_portal(engine_model)
    if not ref:
        ref = blank_credit_reference
    ref = ref.to_portal()
    #ref is a rich CR_Reference object. flatten to primitive for output
    #
    result = [new_model, fixed, ask, ref]
    return result
    
def get_landscape_summary(portal_model, ref_date = None):
    """


    get_landscape_summary(portal_model) -> [PortalModel, LandscapeSummary]


    **API SPEC**

    Function returns a LandscapeSummary for the model, as well as the model.
    """
    schema = {"price" : {"lo" : 0, "hi" : 0},
              "size" : {"lo" : 0, "hi" : 0}}
    #
    engine_model = EngineModel.from_portal(portal_model)
    engine_model, summary = supervisor.summarize_landscape(engine_model,
                                                           ref_date)
    #lower-level modules may send back a new or modified model
    #
    new_model = pm_converter.to_portal(engine_model)
    schema.update(summary)
    #flatten summary down to primitive, try to preserve schema
    #
    result = [new_model, schema]
    return result    

def next_question():
    """


    next_question() -> None


    Function returns the next question from the Engine. Function calls
    step() if Shell is not yet launched, twice otherwise. 
    """
    if not launched:
        step()
    else:
        step()
        step()

def process_interview(msg):
    """


    process_interview(msg) -> PortalMessage


    **API SPEC**

    Function returns engine response to message. Function expects
    ``msg`` to follow the PortalMessage schema specified in the Engine-Wrapper
    API.

    Function converts msg to engine format using to_engine(), gets a new
    response by calling supervisor.process(), converts the response into API
    format, and delivers the converted result. 
    """
    message_for_engine = to_engine(msg)
    engine_response = supervisor.process(message_for_engine)
    message_for_portal = to_portal(engine_response)
    return message_for_portal

def step():
    """


    step() -> None


    Function performs one analytical step.

    Function either:

    1. picks up external messages from Portal and passes them to supervisor
       (downstream) for processing, or
    2. picks up internal messages from supervisor and passes them to Portal
       (upstream) for display and user input. 
    """
    if not launched:
        MR.messageOut = Portal.launch()
        global launched
        launched = True
        return
    if MR.messageOut:
        message_for_engine = to_engine(MR.messageOut)
        MR.messageIn = supervisor.process(message_for_engine)
        MR.messageOut = None
        return
    elif MR.messageIn:
        message_for_portal = to_portal(MR.messageIn)
        MR.messageOut=Portal.process(message_for_portal,
                                         display = show_responses)
        MR.messageIn = None
        return
        
def to_portal(engine_msg):
    """


    to_portal(engine_msg) -> PortalMessage


    Function converts MQR (tuple) messages into dictionaries that comply with
    the PortalMessage schema from Engine-Wrapper API.
    """
    #returns a message that complies w schema
    M = engine_msg[0]
    Q = engine_msg[1]
    R = engine_msg[2]
    #
    global web_mode
    #
    if Q:
        portal_q = QuestionManager.make_portal(Q, web = web_mode)
    else:
        portal_q = Q
    #
    portal_message = dict()
    portal_message["M"] = pm_converter.to_portal(M)
    portal_message["Q"] = portal_q
    portal_message["R"] = R
    return portal_message

def to_engine(portal_msg):
    """


    to_engine(portal_msg) -> MQR


    Function converts messages that comply with the PortalMessage schema from
    Engine-Wrapper API into Engine-compatible MQR tuples.
    """
    portal_model = portal_msg["M"]
    portal_question = portal_msg["Q"]
    portal_response = portal_msg["R"]
    M = EngineModel.from_portal(portal_model)
    #M retains identifying data from portal_model
    Q = portal_question
    R = portal_response
    engine_message = (M,Q,R)
    return engine_message

def use_script(new_script, display=True, trace=False):
    """

    
    use_script(new_script[, display = True[, trace = False]]) -> None


    Function sets module globals ``script`` to new_script and ``show_responses``
    to display. Function then passes the script to SimplePortal.

    SimplePortal expects ``new_script`` to be a dictionary of question names
    that correspond to either
      (i) API-compatible PortalResponse objects or
      (ii) dictionaries in {``response`` = v} format.
    """
    global script
    global show_responses
    script = new_script
    show_responses = display
    Portal.set_script(script)


