#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Shell
"""

Module provides a shell that supports the main Engine services. Shell uses
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
import SimplePortal as Portal
import BBGlobalVariables as Globals

from Controllers import SessionController
from DataStructures.Platform.Messenger import Messenger
from DataStructures.Analysis.PortalModel import PortalModel
from DataStructures.Modelling.Model import Model as EngineModel
from Managers import QuestionManager




#globals
MR = Messenger()

launched = False
low_error = False
script = None
show_responses = False
trace = False
web_mode = True
pm_converter = PortalModel()

QuestionManager.populate()
#QM.populate() should run a no-op here because SessionController or other
#sub modules beat Shell to the punch

#functions
def continuous(max_tries = 200):
    """


    Shell.continuous([max_tries = 200]) -> msg

    
    Function launches Portal and runs a continuous processing loop until Engine
    completes the Model or the number of iterations exceeds the ``max_tries``
    circuit-breaker. Function then returns the last message, always in MQR
    format.
    """
    #
    #run launch routine and first process outside loop
    MR.messageOut = Portal.launch("iop start")
    message_for_engine = to_engine(MR.messageOut)
    MR.messageIn = SessionController.process(message_for_engine)
    last_message = MR.messageIn
    MR.messageOut = None
    #
    #now start looping
    n = 0
    while n < max_tries:
        if MR.messageOut:
            message_for_engine = to_engine(MR.messageOut)
            status = Globals.checkMessageStatus(message_for_engine)
            if status == Globals.status_endSession:
                last_message = message_for_engine
                break
            else:
                MR.messageIn = SessionController.process(message_for_engine)
                MR.messageOut = None
        elif MR.messageIn:
            status = Globals.checkMessageStatus(MR.messageIn)
            if status == Globals.status_endSession:
                last_message = MR.messageIn
                break
            else:
                message_for_portal = to_portal(MR.messageIn)
                MR.messageOut = Portal.process(message_for_portal,
                                                 display = show_responses)
                MR.messageIn = None
        n = n + 1
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

def get_forecast(portal_model, fixed, ask):
    """
    

    get_forecast(portal_model, fixed, ask) -> [CreditReference, PortalModel]


    **API SPEC**

    Function returns a CreditReference that outlines bad, mid, and good
    CreditScenarios. Function may update model during processing. 

    Function first asks SessionController to process analytics for the model,
    then returns the summary of that landscape. Returns blank CreditReference
    on all non-exit exceptions.
    """
    result = None
    M = EngineModel.from_portal(portal_model)
    uM = SessionController.process_analytics(M)
    result = uM.analytics.cc.landscape.forecast(ask = ask, field = fixed)
    return result  
    
def get_landscape_summary(portal_model):
    """


    get_landscape_summary(portal_model) -> [LandscapeSummary, PortalModel]


    **API SPEC**

    Function returns a LandscapeSummary for the model, as well as the model.
    Function may update model during processing.

    Function first asks SessionController to process analytics for the model,
    then returns the summary of that landscape. Returns blank LandscapeSummary
    on all non-exit exceptions.
    """
    result = {"price" : {"lo" : 0, "hi" : 0},
              "size" : {"lo" : 0, "hi" : 0}}
    M = EngineModel.from_portal(portal_model)
    if low_error:
        try:
            M = SessionController.process_analytics(M)
            new_summary = uM.analytics.cc.landscape.getSummary()
            result.update(new_summary)
        except Exception:
            pass
    else:
        #no exception handler
        M = SessionController.process_analytics(M)
        new_summary = uM.analytics.cc.landscape.getSummary()
        result.update(new_summary)
    new_model = pm_converter.to_portal(M)
    return (result, new_model)

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
    response by calling SessionController.process(), converts the response into
    portal format, and delivers the converted result. 
    """
    message_for_engine = to_engine(msg)
    engine_response = SessionController.process(message_for_engine)
    message_for_portal = to_portal(engine_response)
    return message_for_portal

def step():
    """


    step() -> None


    Function performs one analytical step. Function passes portal (external)
    messages to SessionController for processing and engine (internal) messages
    to SimplePortal for display. 
    """
    if not launched:
        MR.messageOut = Portal.launch()
        global launched
        launched = True
        return
    if MR.messageOut:
        message_for_engine = to_engine(MR.messageOut)
        MR.messageIn = SessionController.process(message_for_engine)
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
    portal_message = dict()
    portal_message["M"] = pm_converter.to_portal(M)
    #
    global web_mode
    portal_message["Q"] = QuestionManager.make_portal(Q, web = web_mode)
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


