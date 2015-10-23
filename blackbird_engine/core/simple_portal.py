#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: simple_portal
"""

Module emulates the Blackbird Web Portal and provides messages that contain
user or script responses to Engine questions.

NOTE: Module support caching operations for **debugging purposes only**.

Caching and rewind functionality may differ from Web Portal. Use with caution.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA: 
bb                    str; screen caption for question prompts
cache                 list; processed messages
CACHE_LIMIT           int; maximum number of messages to store
detail_wrapper        obj; instance of TextWrapper object for question details
indent                int; standard indentation
instructions          str; instructions for entering structured responses
instructions_wrapper  obj; instance of TextWrapper object for input instructions
lead_wrapper          obj; instance of TextWrapper object for question prompts
MR                    obj; instance of Messenger object
offset                int; starting message number
PERMIT_CACHING        bool; wheter module supports cache and rewind operations
pr                    str; screen caption for progress indicator
script                dict; object that contains pre-baked responses 
screen_width          int; width of user output in chars, derived from Globals
starting_message      dict; message that Shell can use to start Engine
ux                    str; screen caption for user or script responses
user_attempt_limit    int; max number of responses w bad format for same q
web_mode              bool; if True, Shell returns fully flattened objects

FUNCTIONS:
disable_caching()     turn message storage off, discard cache
enable_caching()      turn message storage on
disable_web_mode()    turns off web mode, permits rich InputElement objects
enable_web_mode()     turns on web mode, requires API-compliant delivery
get_response()        get response to question, either from user or script
go_to()               reprocess specific message from cache, discard others
launch()              run launch routine
process()             get a user response, store input if necessary
rewind()              reprocess message from specified steps back
set_script()          sets script globally
store()               add message to cache

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import textwrap
import time

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.portal.full_question import FullQuestion
from data_structures.portal.portal_model import PortalModel
from data_structures.portal.portal_response import PortalResponse
from data_structures.portal.response_element import ResponseElement
from data_structures.system.messenger import Messenger




#globals
#
blank_model = PortalModel().to_portal()
MR = Messenger()
screen_width = Globals.screen_width - 20
script = None
starting_message = {"M" : blank_model, "Q" : None, "R" : None}
user_attempt_limit = 5
web_mode = True
#
#cache controls
cache = []
CACHE_LIMIT = 100
PERMIT_CACHING = False
offset = 0
#
#strings and formatting
bb = " Blackbird:  "
ux = " User:       "
pr = " Progress:   "
indent = len(bb)
sp = " " * indent
border = " " + "-" * (screen_width - 1)
lead_wrapper = textwrap.TextWrapper(subsequent_indent = sp,
                                    width = screen_width)
detail_wrapper = textwrap.TextWrapper(initial_indent = sp,
                                      subsequent_indent = sp,
                                      width = screen_width)
instructions_wrapper = textwrap.TextWrapper(initial_indent = " ",
                                            subsequent_indent = " ",
                                            width = screen_width)
i = ""
i += "Portal expects dates in YYYY-MM-DD format, time in hh:mm:ss "
i += "format, and ranges in brackets: [a ,b]. To enter multiples values, "
i += "separate values with commas."
i = instructions_wrapper.fill(i)
##i += "\nExample:\n"
##i += "``[1984-11-11, 1996-08-20], [2006-09-01, 2009-06-01]``\n"
instructions = i
#
#get rid of temporary names
del i, sp

#functions
def disable_caching():
    """


    disable_caching() -> None


    Function turns off message storage and deletes all old messages.     
    """
    global cache, PERMIT_CACHING
    PERMIT_CACHING = False
    cache.clear()
    
def disable_web_mode():
    """


    disable_web_mode() -> None


    Function sets turns off web mode: sets module global ``web_mode`` to False.
    
    In web mode, Portal expects inbound messages with fully ``flat`` Q objects,
    where every attribute value is a built-in, JSON compatible object, per the
    Engine-Wrapper API. In particular, in web mode, question["input_array"] is
    a list of plain dictionaries that comply with the API InputElement schema. 

    If web mode is off, Portal expects inbound messages where the question input
    array is a list of instances of **type-specific subclasses** of
    Platform.Analysis.InputElements.GenericInput.
    """
    global web_mode
    web_mode = False

def enable_caching():
    """


    enable_caching() -> None


    Function turns on local storage for processed messages.

    NOTE: simple_portal cache behaviors may differ from web portal.    
    """
    global PERMIT_CACHING
    PERMIT_CACHING = True

def enable_web_mode():
    """


    enable_web_mode() -> None


    Function sets turns on web mode: sets module global ``web_mode`` to True.
    
    In web mode, Portal expects inbound messages with fully ``flat`` Q objects,
    where every attribute value is a built-in, JSON compatible object, per the
    Engine-Wrapper API. In particular, in web mode, question["input_array"] is
    a list of plain dictionaries that comply with the API InputElement schema. 

    If web mode is off, Portal expects inbound messages where the question input
    array is a list of instances of **type-specific subclasses** of
    Platform.Analysis.InputElements.GenericInput.
    """
    global web_mode
    web_mode = True
    
def get_response(message, display = True):
    """


    process(msg[, display = True]) -> PortalMessage


    Function solicits a response to the message it receives as an argument and
    returns a new PortalMessage. Function will get response from user input by
    default, or script when module global ``script`` points to a True object.

    Function expects ``message`` to comply with the PortalMessage schema from
    the Engine-Wrapper API.

    If global ``web_mode`` is False, function will process messages that include
    rich GenericInput-type objects in the question's input array.
    """
    #
    MR.clearMessageOut()
    MR.receive(message)
    M = MR.messageIn["M"]
    Q = MR.messageIn["Q"]
    R = MR.messageIn["R"]
    #
    newR = R
    engine_message_in = (M,Q,R)
    status = Globals.checkMessageStatus(engine_message_in)
    #
    if status != Globals.status_endSession:
        if Q:
            #
            #first check that question fits the Engine-Wrapper API format, then
            #print question.
            #
            #unpack attributes for easier testing:
            q_prompt = Q["prompt"]
            q_comment = Q["comment"]
            q_array_caption = Q["array_caption"]
            progress = Q["progress"]
            question_name = Q["name"]
            input_array = Q["input_array"]
            short = Q["short"]
            number_of_elements = len(input_array)
            multi_element = False
            complex_types = {"date",
                             "date-range",
                             "number-range",
                             "time",
                             "time-range"}
            #
            #check that question is within structural limits
            if not 1 <= number_of_elements <= 5:
                c = "Input array must contain [1,5] input_elements. \n"
                c += "Question ``%s`` contains %s input elements."
                c = c % (question_name, number_of_elements)
                #
                raise BBExceptions.QuestionFormatError(c)
                #
            if number_of_elements > 1:
                multi_element = True
            #
            print("\n\n")
            #
            #print "Q #34: Vendor Concentration"
            if PERMIT_CACHING:
                count = len(cache) + offset
                counter_line = " (Q" + ("#" + str(count)).rjust(4) +") " + short
                counter_line += "\n" + "\n"
                print(counter_line)
                #want to make sure we have the same model id?
                #alternatively, just leave it alone, creates STATE in simple_portal <------------------------------------------------------
                #
            #
            #print question prompt
            q_prompt = bb + q_prompt
            q_prompt = lead_wrapper.fill(q_prompt)
            #wrap long prompts at screen width
            print(q_prompt, "\n")
            if q_comment:
                print(detail_wrapper.fill(q_comment),
                      "\n")
            if q_array_caption:
                print(detail_wrapper.fill(q_array_caption),
                      "\n")
            #
            #prepare to collect a response in the Engine-Wrapper API format. Use
            #a blank PortalResponse object (a list). Portal will manually add
            #response elements for each active input element in Question.
            newR = PortalResponse()
            #
            #In web mode, Shell sends out messages exactly as it would to the
            #Wrapper, per API - in flat dictionaries, with no custom objects.
            #The Wrapper and Web Portal then make sure user responses follow
            #the API schemas.
            #
            #To support user response restrictions in web mode, SimplePortal
            #creates a new instance of FullQuestion every time it encounters
            #a new question. SimplePortal then relies on the methods attached
            #to this instance to create an array of type-specific InputElement
            #objects that will support format verification. SimplePortal updates
            #each element in the ``rich`` FullQuestion input array with
            #data from the matching ``flat`` input element. SimplePortal then
            #delegates verification and printing functions to the ``rich``
            #element. 
            #
            full_q = None
            if web_mode:
                full_q = FullQuestion()
                full_q.set_type(Q["input_type"])
                #
                #<------------------------------------------ yo?
                #
                q_sub_type = Q["input_sub_type"]
                if q_sub_type: 
                    full_q.set_sub_type(q_sub_type)
                #full_q ready, should include an array of type-matched input
                #elements.
                #
                #could just have a FullQuestion.to_engine() that delivers a fully configured
                #Engine object
                #
                #or could walk through input_array and fill out elements
                
            #
            #walk through each question element, get a user / script response
            try:
                for i in range(number_of_elements):
                    input_element = input_array[i]
                    if web_mode:
                        #input_element is a flat dictionary
                        rich_element = full_q.input_array[i]
                        rich_element.__dict__.update(input_element)
                        input_element = rich_element
                        #
                        #<--------------------------------------------------- i dont know what kind of element this is
                    #
                    filled_response = dict()
                    #filled_response = ResponseElement()
                    #
                    #use plain dictionary for response element to track web
                    #portal output; if switch to actual object, change how
                    #Generic InputElement sets values (to obj.__setattr__)
                    #and how Topic.get_first/second_response() work.
                    #
                    element_indent = indent
                    if multi_element:
                        element_header = "\t(Input Element #%s)" % i
                        element_indent = indent + 4
                        print(element_header.expandtabs(indent))
                    print(input_element.__str__().expandtabs(element_indent))
                    loop = True
                    while loop:
                        count = 0
                        try:
                            #get the raw string response, either from script or user
                            if script:
                                user_answer = script[question_name][i]["response"]
                                ux_w_answer = ux + user_answer
                                print(ux_w_answer)
                            else:
                                #
                                if Q["input_type"] in complex_types:
                                    print(instructions)
                                    print("\n")
                                #print user instructions for complex questions
                                #
                                user_answer = input(ux)
                            #
                            #check that response satisfies element
                            if user_answer == Globals.user_stop:
                                raise BBExceptions.UserInterrupt
                            else:
                                input_element.set_response(user_answer,
                                                           target = filled_response)
                                #set_reponse() will run the appropriate format and
                                #verification checks, then record response and input type
                                #on the target
                                #
                                loop = False
                        except BBExceptions.ResponseFormatError as E:
                            print(E)
                            if count < user_attempt_limit:
                                count = count + 1
                                continue
                            else:
                                raise E
                    else:
                        #only get here if loop exited without a break when
                        #``toggled`` to False
                        newR.append(filled_response)
                else:
                    #now that finished collecting user responses, print progress
                    #indicator
                    #
                    #configure progress bar; will print at ``bottom`` of screen,
                    #after user input
                    #
                    pr_max_length = screen_width - len(pr + "||")
                    #include both progress bookends when computing length
                    pr_bar_length = int(progress / 100 * pr_max_length)
                    pr_bar_length = max(1, pr_bar_length)
                    #always show some progress
                    marks = "B" * pr_bar_length
                    spaces  = " " * (pr_max_length - pr_bar_length)
                    pr_indicator = pr + "|" + marks + spaces + "|"
                    #
                    print("\n\n")
                    print(border)
                    print(pr_indicator)
                    print(border)
                    #
            except BBExceptions.UserInterrupt:
                newR = Globals.user_stop
            finally:
                del full_q 
                print("\n")
    else:
        #inbound message signals end session
        print("\n")
        print("We have completed our interview. Thank you.")
        print("Use Blackbird Analytics to explore your market position.")
        print("\n")
        #can write Model to completed database here
    result = {"M": M, "Q": Q, "R": newR}
    MR.messageOut = result
    MR.clearMessageIn()
    #
    return result

def get_element(

def go_to(question_number):
    """


    go_to(question_number) -> message


    Function pulls the message that corresponds to question_number from cache,
    discards any subsequent messages, and returns a re-processed response
    message.

    ``question_number`` should be the number displayed next to the
    ``short_name``. Function will raise error if question falls outside the
    cache range.
    """
    global cache
    #
    i = (question_number - 1) - offset
    if not 0 <= i <= len(cache):
        c = "Requested question falls outside cache range. Cache currently"
        c += "stores messages %s to %y."
        c = c % (offset, len(cache) + offset)
        raise IndexError(c)
    #
    cache = cache[:(i+1)]
    prior_message = cache.pop()
    result = process(prior_message)
    #
    return result

def launch(credentials = ""):
    """


    launch([credentials = ""]) -> PortalMessage


    Function checks if credentials match authorized and returns a blank
    PortalMessage. 
    """
    #Dummy pseudo security
    attempts = 1
    max_attempts = 3
    #
    l1 = "Blackbird Credit Market"
    l1 = l1.center(screen_width)
    l2 = "*"*screen_width+"\n"
    l_rights = "(c) Blackbird Logical Applications, LLC 2015"
    print("\n\n",l2,l1,"\n",l2,l_rights,"\n\n")   
    l_version = " v.0.1"    
    ref_lt = time.localtime()
    ref_date = str(ref_lt.tm_mon).zfill(2)+"/"
    ref_date += str(ref_lt.tm_mday).zfill(2)+"/"
    ref_date += str(ref_lt.tm_year)
    ref_time = str(ref_lt.tm_hour).zfill(2)+":"
    ref_time += str(ref_lt.tm_min).zfill(2)+":"
    ref_time += str(ref_lt.tm_sec).zfill(2)
    l_cal = (" " + ref_date +
             " " * (screen_width - len(ref_date) - len(ref_time)))
    l_cal += ref_time
    print(l_version)
    print(l_cal)
    print("\n\n\n")
    l_welcome = " Welcome to Blackbird"
    print(l_welcome,"\n\n\n")
    a = "iop"
    k = "start"
    if ((a not in credentials) or
        (k not in credentials)):
        l_prompt = " Please enter credentials to begin.\n "
        r = input(l_prompt)
        while k not in r or a not in r:
            if attempts < max_attempts:
                print("\n")
                r = input(" Access denied. Please try again.\n ")
                attempts += 1
                continue
            else:
                locked_out = "You have exceeded the number of permitted attempts. "
                locked_out += "Good bye."
                locked_out = instructions_wrapper.fill(locked_out)
                locked_out = "\n" + locked_out
                print(locked_out)
                #can exit process here
                break
    return starting_message

def process(message, display = True):
    """


    process(message[, display = True]) -> message


    Function gets user response and returns updated message. If caching is on,
    function stores the input message before returning output. 
    """
    if PERMIT_CACHING:
        store(message)
    result = get_response(message, display)
    #
    return result

def rewind(steps_back = 1):
    """


    rewind(steps_back = 1) -> message


    Function runs get_response() on the message that's ``steps_back`` away.
    """
    if not PERMIT_CACHING:
        c = "Portal supports rewind operations only when caching enabled."
        raise BBExceptions.ProcessError(c)
    current_step = len(cache)
    prior_step = current_step - steps_back
    result = go_to(prior_step)
    #
    return result

def set_script(new_script):
    """


    set_script(new_script) -> None


    Function sets module global ``script`` to new_script argument. 
    """
    global script
    script = new_script

def store(msg):
    """


    store(msg) -> None

    
    Function appends message to cache. If cache exceeds size limit, function
    drops the oldest message and increments offset. 
    """
    global cache
    if len(cache) == CACHE_LIMIT:
        cache = cache[1:]
        #discard the oldest message
        global offset
        offset += 1
        #offset the question count that appears in first position in the cache.
        #for example, suppose the cache is limited to 10 entries. you are at q15
        #and want to go back to q8. we know that q15 is at the top of the cache
        #(last poition) because it's the one we saw last. therefore, we know the
        #cache starts at q5, ie q15 - len(cache). offset tracks this
        #information.
    cache.append(msg)
    
