#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\Basic\API_Landscape\Grader
"""
Grader for API_Landscape

Check whether the landscape that Tester delivered includes all required data. 

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
#adding an extra comment line to make sure hg picks up changes
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

        This Grader checks whether the summary of the credit landscape that
        Tester (and Engine) delivered for the known model includes all expected
        data.

        Grader will award an affirmative score ("pass") when new landscape
        summary includes all of the information from the standard summary.
        """
        print(c)
        o = result["output"]
        #18.01:
        print("T18.01: compare landscape summaries.")
        rubric["T18.01: confirmed"] = True
        new_land = o["T18.01"]["new land"]
        std_land = standard["T18.01"]["new land"]
        print("""
        new_land = o["T18.01"]["new land"]
        std_land = standard["T18.01"]["new land"]
        """)
        print("new_land: \n%s\n" % new_land)
        print("std_land: \n%s\n" % std_land)
        #
        known_keys = sorted(std_land.keys())
        #maintain fixed order of keys
        print("""
        known_keys = sorted(std_land.keys())
        """)
        print("Known keys: \n", known_keys)
        c = """

        Iterate through known_keys, check that values in new summary
        match those in known message. New summary may include additional
        (key, value) pairs and still pass the test.

        Test still requires that each attribute in the landscape summary
        conform to the API spec and include **only** the ``hi`` and ``lo``
        keys.
        """
        print(c)
        #
        outcome = True
        for (i,k) in enumerate(known_keys):
            known_value = std_land[k]
            new_value = new_land[k]
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
            print("New landscape summary includes all expected data: ", False)
            rubric["T18.01.01: landscape summaries match"]=False
            rubric["T18.01: confirmed"] = False
        else:
            print("New landscape summary includes all expected data: ", True)
            rubric["T18.01.01: landscape summaries match"]=True
        #
        print("T18.01 finished. \n\n")
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
                print("API_Landscape passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("API_Landscape passed: ", True)
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
