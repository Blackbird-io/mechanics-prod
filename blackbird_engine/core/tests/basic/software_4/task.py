#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.software_4.Task
"""
Task Module

SCRIPT: software_4_by_seat_no_devs

Run through scripted interview using only API interface, return last message,
store string views of current period and company financials for comparison.

NOTE: Test **discards** e-model prior to returning result.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
output                dict; populated on do()
active_script         dict; from seed.answers

FUNCTIONS:
do()                  runs through interview, populates output

CLASSES: 
n/a
====================  ==========================================================
"""




#imports
import Shell as Engine
import simple_portal as Portal

from tools import for_messages as message_tools

from scripts import software_4_by_seat_no_devs as seed


from collections import OrderedDict



#globals
output = OrderedDict()
active_script = seed.answers

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
    c = ""
    c+= "Use script: \n%s\n" % active_script
    print(c)
    #
    Portal.set_script(active_script)
    c = """Portal.set_script(active_script)"""
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
        status = message_tools.checkMessageStatus(msg_mqr)
        if status == message_tools.status_endSession:
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
    output["1. final message"] = final_message
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
    c = """


    Now store stateless string views of company financials for current period
    and the current period iteself. Grader will compare these to standard too.

    Pull both Blackbird objects from an engine-format conversion of the final
    message.
    """
    print(c)
    final_mqr = Engine.to_engine(final_message)
    model = final_mqr[0]
    model.time_line.extrapolate()

    #   current period
    current_period = model.time_line.current_period
    company = current_period.content
    output["2. current period"] = str(current_period)
    output["3. company financials"] = str(company.financials)

    all_periods = model.time_line.get_ordered()
    last_period = all_periods[-1]

    mid_point = current_period.end + (last_period.end - current_period.end)/2.
    mid_period = model.time_line.find_period(mid_point)

    #   future period (mid-point between current and last period)
    company = mid_period.content
    output["4. future period (mid-point)"] = str(mid_period)
    output["5. company financials"] = str(company.financials)

    #   future period (last, period furthest into the future)
    company = last_period.content
    output["6. future period (last)"] = str(last_period)
    output["7. company financials"] = str(company.financials)

    c = """


    Discard PortalModel[``e_model``] to keep output compact.
    """
    print(c)
    final_message["M"].pop("e_model")
    #
    return output
    #
    #
    #













