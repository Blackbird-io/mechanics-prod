#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.interview_test_template.Grader
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

from .__init__ import name as test_name
from tests.tools import walk_dict




#globals
generic_label = "Build passes test: "
custom_label = "Build passes ``%s`` test:  "
success_label = generic_label
if test_name:
    custom_label = custom_label % test_name
    success_label = custom_label

#functions
def printRubric(r, width = 60):
    """


    printRubric(r[, width = 60]) -> tuple


    Function prints the Grader rubric nicely and returns a tuple of results.
    """
    print("RUBRIC:\n")
    ks = list(r.keys())
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
        print(k, dots, r[k])
    return (stepks, confks)

def check(result,standard):
    """


    check(result, standard) -> tuple


    Function checks whether result satisfies standard. Returns bool result
    and scoring rubric. 
    """
    #
    #standard is a stored version of the ``perfect`` output, w symmetrical
    #keys
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        c = """

        This Grader checks whether the Engine delivered output that matches
        expectations for a known set of inputs.
        
        """
        print(c)
        #T.01:
        print("T.01: compare output.")
        rubric["T.01: confirmed"] = True
        #
        new_output = result["output"]
        std_output = standard["output"]
        #
        print("""
        new_output = result["output"]
        std_output = standard["output"]
        """)
        #
        c = """

        Check that new output contains all of the standard data. New output can
        pass test when it supplements expected data with additional information.
        
        """
        print(c)
        #
        c = """

        outcome = walk_dict(std_output, new_output)
        
        """
        print(c)
        outcome = walk_dict(std_output, new_output)
        #
        if not outcome:
            print("New output includes expected data: ", False)
            rubric["T01.01: new includes standard"]=False
            rubric["T.01: confirmed"] = False
        else:
            print("New output includes expected data: ", True)
            rubric["T.01.01: new includes standard"]=True
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
                print(success_label, False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print(success_label, True)
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
        stepks, confks = printRubric(r=rubric)
        passed = False
        print("passed set to False by Grader")
    finally:
        return (passed,rubric)
