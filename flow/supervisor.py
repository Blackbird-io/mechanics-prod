# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Engine
# Module: flow.supervisor
"""

Module supervises how the Engine performs substantive work.

Conceptually, the Engine works by exchanging raw information it gets through
Shell for processed information it produces. Supervisor sits directly below
Shell. Shell calls supervisor whenever Shell receives a message (``message A``).
Supervisor figures out a new message in response (``message B``) and returns it
to Shell.

Shell then passes message B to Portal. Portal combines message B with user input
to form ``message C``. Portal then hands off message C back to Shell, Shell
passes message C to supervisor, and so on.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
MR                    obj; instance of Messenger, stores current message

FUNCTIONS:
check_started()       returns True if message model is started, else False
process()             returns next message from Engine

CLASSES:
n/a
====================  ==========================================================
"""




# Imports
from data_structures.system.messenger import Messenger

from .analyst import Analyst
from .starter import Starter




# Constants
# n/a

# Other Globals
MR = Messenger()


# Functions
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

    Function delegates all substantive work to junior modules. For messages that
    are empty (msg == (None, None, None)) or signal the start of an interview
    under the Engine-Wrapper API, function delegates work to starter. For all
    other messages, function delegates work to an analyst.

    To allow admin to look inside the function-time operation, function stores
    message_in on MR. Function clears MR at the beginning of each call.
    """
    # Function makes a fresh analyst for every call. This approach helps keep
    # engine completely stateless. The analyst delegates to topics as necessary
    # and then unilaterally determines when the model is done. The analyst
    # returns messages with user-facing questions and a final (M,_,END) with the
    # completed model.
    #
    MR.prep(message)
    # only purpose of MR here is to allow an admin to look inside the engine at
    # run time and see what went in/came out.
    #
    if not check_started(message):
        grant_hill = Starter()
        message = grant_hill.process(message)
    #
    seth_klarman = Analyst()
    message = seth_klarman.process(message)
    MR.clear()

    return message

