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
CACHE_LIMIT           int; maximum number of messages to store
SCREEN_WIDTH          int; width of user output in chars
USER_ATTEMPT_LIMIT    int; max number of responses w bad format for same q
USER_STOP             str; hard break sequence
BB                    str; screen caption for question prompts
PR                    str; screen caption for progress indicator
UX                    str; screen caption for user or script responses

FUNCTIONS:
disable_caching()     turn message storage off, discard cache
enable_caching()      turn message storage on
go_to()               reprocess specific message from cache, discard others
launch()              run launch routine
process()             get a user response, store input if necessary
rewind()              reprocess message from specified steps back
set_script()          sets script

CLASSES:
n/a
====================  ==========================================================
"""




# Imports
import time

import bb_exceptions
import bb_settings as Globals

from data_structures.portal.full_question import FullQuestion
from data_structures.portal.portal_model import PortalModel
from data_structures.portal.portal_response import PortalResponse
from data_structures.portal.response_element import ResponseElement
from data_structures.system.messenger import Messenger

from tools import for_messages as message_tools

from textwrap import TextWrapper




# Constants
CACHE_LIMIT = 100
SCREEN_WIDTH = Globals.SCREEN_WIDTH - 20
USER_ATTEMPT_LIMIT = 5
USER_STOP = message_tools.USER_STOP
#
BB = " Blackbird:  "
UX = " User:       "
PR = " Progress:   "

# Other Globals
#cache controls
cache = []
cache_offset = 0
permit_caching = False

#other state
MR = Messenger()
script = None
blank_model = PortalModel().to_portal()
starting_message = {"M" : blank_model, "Q" : None, "R" : None}

#formatting
border = " " + "-" * (SCREEN_WIDTH - 1)
indent = len(BB)
left_margin = " " * indent
#
wrapper_lead = TextWrapper(subsequent_indent=left_margin,
                           width=SCREEN_WIDTH)
wrapper_detail = TextWrapper(initial_indent=left_margin,
                             subsequent_indent=left_margin,
                             width=SCREEN_WIDTH)
wrapper_instructions = TextWrapper(initial_indent=" ",
                                   subsequent_indent=" ",
                                   width=SCREEN_WIDTH)
#
instructions = """
Portal expects dates in YYYY-MM-DD format, time in hh:mm:ss

format, and ranges in brackets: [a ,b]. To enter multiples values, 
separate values with commas.
"""
instructions = wrapper_instructions.fill(instructions)
##instructions += "\nExample:\n"
##instructions += "``[1984-11-11, 1996-08-20], [2006-09-01, 2009-06-01]``\n"

# Functions

def disable_caching():
    """


    disable_caching() -> None


    Function turns off message storage and deletes all old messages.     
    """
    global cache, permit_caching
    permit_caching = False
    cache.clear()
    
def enable_caching():
    """


    enable_caching() -> None


    Function turns on local storage for processed messages.

    NOTE: simple_portal cache behaviors may differ from web portal.    
    """
    global permit_caching
    permit_caching = True
        
def go_to(question_number):
    """


    go_to() -> message


    Function pulls the message that corresponds to question_number from cache,
    discards any subsequent messages, and returns a re-processed response
    message.

    ``question_number`` should be the number displayed next to the
    ``short_name``. Function will raise error if question falls outside the
    cache range.
    """
    global cache
    #
    i = (question_number - 1) - cache_offset
    if not 0 <= i <= len(cache):
        c = "Requested question falls outside cache range. Cache currently"
        c += "stores messages %s to %y."
        c = c % (cache_offset, len(cache) + cache_offset)
        raise IndexError(c)
    #
    cache = cache[:(i+1)]
    prior_message = cache.pop()
    result = process(prior_message)
    #
    return result

def launch(credentials=""):
    """


    launch() -> PortalMessage


    Function checks if credentials match authorized and returns a blank
    PortalMessage. 
    """
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
                locked_out = wrapper_instructions.fill(locked_out)
                locked_out = "\n" + locked_out
                print(locked_out)
                #can exit process here
                break
    #
    return starting_message

def process(message, display=True):
    """


    process() -> message


    Function gets user response and returns updated message. If caching is on,
    function stores the input message before returning output. 
    """
    if permit_caching:
        _store(message)
    result = _respond_to_message(message)
    #
    return result

def rewind(steps_back=1):
    """


    rewind() -> message


    Function runs get_response() on the message that's ``steps_back`` away.
    """
    if not permit_caching:
        c = "Portal supports rewind operations only when caching enabled."
        raise bb_exceptions.ProcessError(c)
    current_step = len(cache)
    prior_step = current_step - steps_back
    result = go_to(prior_step)
    #
    return result

def set_script(new_script):
    """


    set_script() -> None


    Function sets module global ``script`` to new_script argument. 
    """
    global script
    script = new_script

#*****************************************************************************#
#                            NON-PUBLIC FUNCTIONS                             #
#*****************************************************************************#

def _get_scripted_response(rich_element, position, response_array):
    """


    _get_scripted_response() -> str or None


    Return response to element from script. Search by caption first; if no
    element matches, pull response by position.
    """

    scripted_response = None

    k_caption = "main_caption"
    k_response = "response"
    # Store keys in vars to avoid silently passing over typos with dict.get()
    
    target_caption = rich_element.main_caption

    for response_element in response_array:
        
        if response_element.get(k_caption) == target_caption:
            # Found the right element
            scripted_response = response_element[k_response]
            break
        else:
            continue

    else:
        # No matching caption, probably because script does not include caption
        # names. Pull the response by index.
        scripted_response = response_array[position][k_response]

    return scripted_response
    
def _print_progress_bar(progress):
    """


    _print_progress_bar() -> None


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

def _respond_to_element(element, question_name, position, response_array=None):
    """


    _respond_to_element() -> ResponseElement

    
    Return ResponseElement dictionary with either user or script input.

    If input doesn't match element requirements, repeat up to
    USER_ATTEMPT_LIMIT, then raise ResponseFormatError. 
    """
    result = dict()
    #
    complex_types = {"date",
                     "date-range",
                     "number-range",
                     "time",
                     "time-range"}
    loop = True
    count = 0
    while loop:
        try:
            # First, get the raw response string
            if script:
                user_answer = _get_scripted_response(element, position,
                                                     response_array)
                ux_w_answer = UX + user_answer
                print(ux_w_answer)
            else:
                if element.input_type in complex_types:
                    print(instructions)
                    print("\n")
                user_answer = input(UX)
            
            # Second, check that response satisfies element
            if user_answer == USER_STOP:
                raise bb_exceptions.UserInterrupt
            else:
                element.set_response(user_answer, target=result)
                # set_response() runs formats the response, verifies that it fits
                # type requirements, and then records it in target. Call will
                # raise a ResponseFormatError if there is any trouble
                #
                loop = False
                #
        except bb_exceptions.ResponseFormatError as E:
            # Catch only format-related exceptions
            print(E)
            count +=1
            if count < USER_ATTEMPT_LIMIT:
                continue
            else:
                raise E
    #
    return result

def _respond_to_message(message):
    """


    _respond_to_message() -> PortalMessage


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
    status = message_tools.checkMessageStatus(engine_message_in)
    #
    if status != message_tools.status_endSession:
        if Q:
            newR = PortalResponse()
            conditional = False
            
            array_caption = Q["array_caption"]
            comment = Q["comment"]
            input_array = Q["input_array"].copy()
            # Copy here to make sure we don't change the original
            name = Q["name"]
            progress = Q["progress"]
            prompt = Q["prompt"]
            short = Q["short"]
            gating_element = Q["show_if"]

            if gating_element is not None:
                conditional = True
                input_array.insert(0, gating_element)
                # Put the gating element into the array so we can process all
                # of the elements together. Adjusted to track Web Portal per
                # case 563.
            
            number_of_elements = len(input_array)
            multi_element = False
            element_indent = indent
            if number_of_elements > 1:
                multi_element = True
                element_indent = indent + 4
            
            print("\n\n")
            if permit_caching:
                count = len(cache) + cache_offset
                counter_line = " (Q" + ("#" + str(count)).rjust(4) +") " + short
                counter_line += "\n" + "\n"
                print(counter_line)
                # Prints something like ``Q #34: Vendor Concentration``
            
            prompt = BB + prompt
            prompt = wrapper_lead.fill(prompt)
            print(prompt, "\n")
            
            if comment:
                print(wrapper_detail.fill(comment), "\n")
            if array_caption:
                print(wrapper_detail.fill(array_caption), "\n")
            
            full_q = FullQuestion()
            full_q.build_custom_array(input_array,
                                      Q["input_type"],
                                      Q["input_sub_type"],
                                      ignore_fixed=True)
            # Input_array contains flat dictionaries in JSON. We can turn use
            # full_q to automatically create matching rich element objects that
            # can then do their own response validation.
            
            try:
                for i in range(number_of_elements):

                    rich_element = full_q.input_array[i]
                    #
                    if multi_element:
                        element_header = "\t(Input Element #%s)" % i
                        print(element_header.expandtabs(indent))
                    print(rich_element.__str__().expandtabs(element_indent))

                    # GET RESPONSE ARRAY HERE
                    response_arr = None
                    if script:
                        try:
                            response_arr = script[Q["prompt"]]
                        except KeyError:
                            response_arr = script[name]

                    element_response = _respond_to_element(rich_element, name,
                                                           i, response_arr)
                    newR.append(element_response)
                    #
                    if conditional:
                        # Check if user should see the other elements. Gating
                        # element always goes first in the array, so only do the
                        # check for index 0.
                        if i == 0:
                            words = element_response["response"][0]
                            if words == rich_element.toggle_caption_true:
                                continue
                            else:
                                break
                            
                # Loop over, filled out the response, print progress bar
                _print_progress_bar(progress)
                
            except bb_exceptions.UserInterrupt:
                newR = USER_STOP
                
            finally:
                del full_q 
                print("\n")
    else:
        # Inbound message signals end session
        print("\n")
        print("We have completed our interview. Thank you.")
        print("Use Blackbird Analytics to explore your market position.")
        print("\n")
        # Can write Model to completed database here
        
    result = {"M": M, "Q": Q, "R": newR}
    MR.messageOut = result
    MR.clearMessageIn()
    
    return result

def _store(message):
    """


    store() -> None

    
    Function appends message to cache. If cache exceeds size limit, function
    drops the oldest message and increments cache_offset. 
    """
    global cache
    if len(cache) == CACHE_LIMIT:
        cache = cache[1:]
        #discard the oldest message
        global cache_offset
        cache_offset += 1
        # Offset the question count that appears in first position in the cache.
        # For example, suppose the cache is limited to 10 entries.  You are at
        # q15 and want to go back to q8. we know that q15 is at the top of the
        # cache (last position) because it's the one we saw last.  Therefore, we
        # know the cache starts at q5, ie q15 - len(cache). cache_offset tracks
        # this information.
    cache.append(message)

    
