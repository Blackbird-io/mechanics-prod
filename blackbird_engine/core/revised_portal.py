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
BB                    str; screen caption for question prompts
CACHE                 list; processed messages
CACHE_LIMIT           int; maximum number of messages to store
CACHE_OFFSET          int; starting message number
INDENT                int; left margin size
INSTRUCTIONS          str; instructions for entering structured responses
MR                    obj; instance of Messenger object
WRAPPER_DETAILS       obj; instance of TextWrapper object for question details
WRAPPER_INSTRUCTIONS  obj; instance of TextWrapper object for input instructions
WRAPPER_LEAD          obj; instance of TextWrapper object for question prompts


PERMIT_CACHING        bool; wheter module supports cache and rewind operations
pr                    str; screen caption for progress indicator
SCREEN_WIDTH          int; width of user output in chars
SCRIPT                dict; object that contains pre-baked responses 

UX                    str; screen caption for user or script responses
USER_ATTEMPT_LIMIT    int; max number of responses w bad format for same q

FUNCTIONS:
disable_caching()     turn message storage off, discard cache
enable_caching()      turn message storage on
get_response()        get response to question, either from user or script
go_to()               reprocess specific message from cache, discard others
launch()              run launch routine
process()             get a user response, store input if necessary
rewind()              reprocess message from specified steps back
set_script()          sets SCRIPT
store()               add message to cache

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import time

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.portal.full_question import FullQuestion
from data_structures.portal.portal_model import PortalModel
from data_structures.portal.portal_response import PortalResponse
from data_structures.portal.response_element import ResponseElement
from data_structures.system.messenger import Messenger

from textwrap import TextWrapper




#globals
PERMIT_CACHING = False
SCREEN_WIDTH = 60
USER_ATTEMPT_LIMIT = 5
USER_STOP = "STOP INTERVIEW"

#cache controls
CACHE = []
CACHE_LIMIT = 100
CACHE_OFFSET = 0

#other state
MR = Messenger()
SCRIPT = None

#strings and formatting
BB = " Blackbird:  "
UX = " User:       "
PR = " Progress:   "
#
BORDER = " " + "-" * (SCREEN_WIDTH - 1)
INDENT = len(BB)
LEFT_MARGIN = " " * INDENT
#
WRAPPER_LEAD = TextWrapper(subsequent_indent = LEFT_MARGIN, width = SCREEN_WIDTH)
WRAPPER_DETAIL = TextWrapper(initial_indent = LEFT_MARGIN,
                             subsequent_indent = LEFT_MARGIN,
                             width = SCREEN_WIDTH)
WRAPPER_INSTRUCTIONS = TextWrapper(initial_indent = " ",
                                   subsequent_indent = " ",
                                   width = SCREEN_WIDTH)
#
INSTRUCTIONS = """
Portal expects dates in YYYY-MM-DD format, time in hh:mm:ss
format, and ranges in brackets: [a ,b]. To enter multiples values, 
separate values with commas.
"""
INSTRUCTIONS = WRAPPER_INSTRUCTIONS.fill(i)
##INSTRUCTIONS += "\nExample:\n"
##INSTRUCTIONS += "``[1984-11-11, 1996-08-20], [2006-09-01, 2009-06-01]``\n"

#functions
def disable_caching():
    """


    disable_caching() -> None


    Function turns off message storage and deletes all old messages.     
    """
    global CACHE, PERMIT_CACHING
    PERMIT_CACHING = False
    CACHE.clear()
    
def enable_caching():
    """


    enable_caching() -> None


    Function turns on local storage for processed messages.

    NOTE: simple_portal cache behaviors may differ from web portal.    
    """
    global PERMIT_CACHING
    PERMIT_CACHING = True
    
def get_response(message):
    """


    get_response(message) -> PortalMessage


    Function solicits a response to the message it receives as an argument and
    returns a new PortalMessage. Function will get response from user input by
    default, or script when module global ``SCRIPT`` points to a True object.

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
            newR = PortalResponse()
            #
            array_caption = Q["array_caption"]
            comment = Q["comment"]
            conditional = Q["conditional"]
            input_array = Q["input_array"]
            name = Q["name"]
            prompt = Q["prompt"]
            short = Q["short"]
            #
            number_of_elements = len(input_array)
            multi_element = False
            element_indent = INDENT
            if number_of_elements > 1:
                multi_element = True
                element_indent = INDENT + 4
            #
            print("\n\n")
            if PERMIT_CACHING:
                count = len(CACHE) + CACHE_OFFSET
                counter_line = " (Q" + ("#" + str(count)).rjust(4) +") " + short
                counter_line += "\n" + "\n"
                print(counter_line)
                #prints "Q #34: Vendor Concentration"
            #
            prompt = BB + prompt
            prompt = WRAPPER_LEAD.fill(prompt)
            print(prompt, "\n")
            #
            if comment:
                print(WRAPPER_DETAIL.fill(comment), "\n")
            if array_caption:
                print(WRAPPER_DETAIL.fill(array_caption), "\n")
            #
            full_q = FullQuestion()
            full_q.build_custom_array(input_array)
            #input_array contains flat dictionaries; use full_q to turn it into a
            #list of rich objects that can do their own response checking.
            try:
                for i in range(number_of_elements):
                    rich_element = full_q.input_array[i]
                    #
                    if multi_element:
                        element_header = "\t(Input Element #%s)" % i
                        print(element_header.expandtabs(INDENT))
                    print(rich_element.__str__().expandtabs(element_indent))
                    #
                    element_response = respond_to_element(rich_element, name)
                    newR.append(element_response)
                    #
                    if conditional:
                        if element_response == rich_element.toggle_caption_true:
                            continue
                        else:
                            break
                #filled out the response, print progress bar
                print_progress_bar(Q["progress"])
            except BBExceptions.UserInterrupt:
                newR = USER_STOP
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

def respond_to_element(element, question_name):
    """
    -> dict()

    """
    result = dict()
    #
    complex_types = {"date",
                     "date-range",
                     "number-range",
                     "time",
                     "time-range"}
    loop = True
    while loop:
        try:
            #first, get the raw response string
            if SCRIPT:
                user_answer = SCRIPT[question_name][i]["response"]
                ux_w_answer = UX + user_answer
                print(ux_w_answer)
            else:
                if element.input_type in complex_types:
                    print(INSTRUCTIONS)
                    print("\n")
                user_answer = input(UX)
            #
            #second, check that response satisfies element
            if user_answer == USER_STOP:
                raise BBExceptions.UserInterrupt
            else:
                element.set_response(user_answer, target = result)
                #set_response() runs formats the response, verifies that it fits
                #type requirements, and then records it in target. call will
                #raise a ResponseFormatError if there is any trouble
                #
                loop = False
                #
        except BBExceptions.ResponseFormatError as E:
            #catch only format-related exceptions
            print(E)
            if count < USER_ATTEMPT_LIMIT:
                count += 1
                continue
            else:
                raise E
    #
    return result

def print_progress_bar(progress):
    """


    print_progress_bar(progress) -> None


    Print progress bar. Expects ``progress`` to be int in [0,100].
    """
    pr_max_length = SCREEN_WIDTH - len(PR + "||")
    #include both progress bookends when computing length
    pr_bar_length = int(progress / 100 * pr_max_length)
    pr_bar_length = max(1, pr_bar_length)
    #always show some progress
    marks = "B" * pr_bar_length
    spaces  = " " * (pr_max_length - pr_bar_length)
    pr_indicator = PR + "|" + marks + spaces + "|"
    #
    print("\n\n")
    print(border)
    print(pr_indicator)
    print(border)
    
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
    global CACHE
    #
    i = (question_number - 1) - CACHE_OFFSET
    if not 0 <= i <= len(CACHE):
        c = "Requested question falls outside CACHE range. Cache currently"
        c += "stores messages %s to %y."
        c = c % (CACHE_OFFSET, len(CACHE) + CACHE_OFFSET)
        raise IndexError(c)
    #
    CACHE = CACHE[:(i+1)]
    prior_message = CACHE.pop()
    result = process(prior_message)
    #
    return result

def launch(credentials = ""):
    """


    launch([credentials = ""]) -> PortalMessage


    Function checks if credentials match authorized and returns a blank
    PortalMessage. 
    """
    #
    blank_model = PortalModel().to_portal()
    starting_message = {"M" : blank_model, "Q" : None, "R" : None}
    #
    #Dummy pseudo security
    attempts = 1
    max_attempts = 3
    #
    l1 = "Blackbird Engine"
    l1 = l1.center(SCREEN_WIDTH)
    l2 = "*" * SCREEN_WIDTH + "\n"
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
             " " * (SCREEN_WIDTH - len(ref_date) - len(ref_time)))
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
                locked_out = WRAPPER_INSTRUCTIONS.fill(locked_out)
                locked_out = "\n" + locked_out
                print(locked_out)
                #can exit process here
                break
    #
    return starting_message

def process(message, display = True):
    """


    process(message[, display = True]) -> message


    Function gets user response and returns updated message. If caching is on,
    function stores the input message before returning output. 
    """
    if PERMIT_CACHING:
        store(message)
    result = get_response(message)
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
    current_step = len(CACHE)
    prior_step = current_step - steps_back
    result = go_to(prior_step)
    #
    return result

def set_script(new_script):
    """


    set_script(new_script) -> None


    Function sets module global ``SCRIPT`` to new_script argument. 
    """
    global SCRIPT
    SCRIPT = new_script

def store(msg):
    """


    store(msg) -> None

    
    Function appends message to CACHE. If CACHE exceeds size limit, function
    drops the oldest message and increments CACHE_OFFSET. 
    """
    global CACHE
    if len(CACHE) == CACHE_LIMIT:
        CACHE = CACHE[1:]
        #discard the oldest message
        global CACHE_OFFSET
        CACHE_OFFSET += 1
        #CACHE_OFFSET the question count that appears in first position in the CACHE.
        #for example, suppose the CACHE is limited to 10 entries. you are at q15
        #and want to go back to q8. we know that q15 is at the top of the CACHE
        #(last poition) because it's the one we saw last. therefore, we know the
        #CACHE starts at q5, ie q15 - len(CACHE). CACHE_OFFSET tracks this
        #information.
    CACHE.append(msg)
    
