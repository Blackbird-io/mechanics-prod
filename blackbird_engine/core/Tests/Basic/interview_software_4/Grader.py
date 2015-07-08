#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.interview_template.Grader
"""
Grader for interview_template

Check whether concluding message includes all of the expected data. 

====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
check()               compare Task output to standard
printRubric()         pretty print for performance results

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import sys
import traceback




#globals
#n/a

#functions
def printRubric(r, width = 60):
    print("RUBRIC:\n")
    ks = list(rubric.keys())
    ks.sort()
    stepks = []
    confks = []
    for k in ks:
        if k.endswith("confirmed"):
            confks.append(k)
        else:
            stepks.append(k)
    for k in ks:
        dots = "."*(width-len(k))
        print(k,dots,rubric[k])
    return (stepks,confks)


def check(result,standard):
    #standard is a stored version of the ``perfect`` output, w symmetrical
    #keys
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        c = """

        This Grader checks whether the contents of the message that the Engine
        returns at the conclusion of a simple scripted interview include all
        of the required data from a standard end-of-interview message.

        This Grader uses a standard message with a **deleted** e_model to
        remain neutral towards model structure. 
        
        Grader will award an affirmative score ("pass") for all new messages
        that include the entirety of information from known summaries.
        """
        print(c)
        o = result["output"]
        #17.01:
        print("T.01: compare concluding messages.")
        rubric["T.01: confirmed"] = True
        new_msg = o["T.01"]["final message"]
        #
        std_msg = standard["T.01"]["final message"]
        print("""
        new_msg = o["T.01"]["final message"]
        std_msg = standard["T.01"]["final message"]
        """)
        print("new_msg: \n%s\n" % new_msg)
        print("std_msg: \n%s\n" % std_msg)
        #
        known_keys = sorted(std_msg.keys())
        #maintain fixed order of keys
        print("""
        known_keys = sorted(std_msg.keys())
        """)
        print("Known keys: \n", known_keys)
        c = """
        Iterate through known_keys, check that values in new message
        match those in known message. New summary may include additional
        data and still pass the test.
        """
        print(c)
        #
        outcome = True
        for (i,k) in enumerate(known_keys):
            known_value = std_msg[k]
            new_value = new_msg[k]
            c = ""
            c += "%s. Key: %s\n" % (i,k)
            c += "\tKnown value: %s\n" % known_value
            c += "\tNew value:   %s\n" % new_value
            print(c)
            if known_value != new_value:
                print("known value != new value")
                outcome = False
            else:
                continue
        else:
            print("\n")
        if not outcome:
            print("New message includes all expected data: ", False)
            rubric["T.01.01: summaries match"]=False
            rubric["T.01: confirmed"] = False
        else:
            print("New message includes all expected data: ", True)
            rubric["T.01.01: summaries match"]=True
        #
        print("T.01 finished. \n\n")
        #
        #
        #check rubric, figure out result
        #this test requires 100% accuracy, so decision criterion is simple
        stepks,confks = printRubric(r = rubric)
        for k in confks:
            if rubric[k] == False:
                passed = False
                print("*"*80)
                print("*"*80)
                print(k, " ", rubric[k])
                print("Test passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("Test passed: ", True)
            print("*"*80)
            print("*"*80)
    except Exception as X:
        #note general failure; rubric should contain details
        print("\n")
        print("!!! GRADER INTERCEPTED EXCEPTION !!!")
        print(X)
        print("running traceback functions")
        traceback.print_exc(file = sys.stdout)
        traceback.print_stack(file = sys.stdout)
        print("\n")
        stepks,confks = printRubric(r=rubric)
        passed = False
        print("passed set to False by Grader")
    finally:
        print("Grader level: ")
        print("Passed: ", passed)
        return (passed,rubric)
