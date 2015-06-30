#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.API_Interview.Task
"""
Task for API_Interview

Run through scripted interview using only API interface, return last message. 

====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
output                dict; populated on do()
retail_script         dict; from Retail2_Raw.answers

FUNCTIONS:
do()                  runs through interview, populates output

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals
import Shell as Engine
import SimplePortal as Portal

from Scripts import retail_2_ext




#globals
output = {}
retail_script = retail_2_ext.answers

#functions
def do():
    """


    Task.do() -> dict()

    
    NOTE: Task.do() must always return output.

    Output is usually a dictionary of data. Output can be any object that the
    Grader for this Test understands

    Function runs through an interview script until Engine declares completion. 
    """
    #
    #T17.01
    #
    c = ""
    c+= "Use script: \n%s\n" % retail_script
    print(c)
    #
    Portal.set_script(retail_script)
    c = """Portal.set_script(retail_script)"""
    print(c)
    #
    msg_0 = Portal.starting_message
    c = ""
    c+= "msg_0 = Portal.starting_message"
    c+= "\nStarting message: \n%s\n" % msg_0
    print(c)
    #
    final_message = None
    c = "final_message = None"
    print(c)
    #
    c = """
    Start with a blank portal message. Call Engine through the API interface for
    the next message. Use the Simple Portal to process the engine output. Repeat
    until Engine returns an end-interview message.
    
    For any message, Portal will collect the user response (here, from the
    script), package the response into an API-spec PortalResponse object, and
    return a new, conforming message.

    Use the Engine's checkMessageStatus function to figure out when to stop.
    """
    print(c)
    #
    loop = True
    while loop:
        msg_1 = Engine.process_interview(msg_0)
        msg_mqr = Engine.to_engine(msg_1)
        #
        status = Globals.checkMessageStatus(msg_mqr)
        if status == Globals.status_endSession:
            final_message = msg_1
            break
        else:
            msg_2 = Portal.process(msg_1)
            msg_0 = msg_2
            continue
    
    c+= """
    loop = True
    while loop:
        msg_1 = Engine.process_interview(msg_0)
        msg_mqr = Engine.to_engine(msg_1)
        #
        status = Globals.checkMessageStatus(msg_mqr)
        if status == Globals.status_endSession:
            final_message = msg_1
            break
        else:
            msg_2 = Portal.process(msg_1)
            msg_0 = msg_2
            continue
    """
    print(c)
    output["T17.01"] = {}
    output["T17.01"]["final message"] = final_message
    #
    c = """
    Engine successfully concluded the interview and stored the final message
    for grading. 

    Test does not print final_message because it contains a long string for the
    serialized e_model.

    Grader will individually evaluate whether the final message satisfies the
    standard. 
    """
    print(c)
    #
    #
    return output
    #
    #
    #













