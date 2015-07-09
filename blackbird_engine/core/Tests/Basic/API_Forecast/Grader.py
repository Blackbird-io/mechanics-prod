#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\Basic\API_Forecast\Grader
"""
Grader for API_Forecast

Check whether new references match standards for the same price/size point. 
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

from ..testing_tools import walk_dict




#globals
#n/a

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

        This Grader checks whether the Engine delivered a set of credit
        references that matches expectations for a known model.
        
        """
        print(c)
        o = result["output"]
        #19.01:
        print("T19.01: compare credit references.")
        rubric["T19.01: confirmed"] = True
        #
        new_references = o["T19.01"]["references"]
        std_references = standard["T19.01"]["references"]
        #
        print("""
        new_references = o["T19.01"]["references"]
        std_references = standard["T19.01"]["references"]
        """)
        #
        c = """

        Check that new credit references contain all of the standard data. New
        references can pass even when they contain additional data (that does
        not exist in old references).
        
        """
        print(c)
        #
        c = """

        outcome = walk_dict(std_references, new_references)
        
        """
        print(c)
        outcome = walk_dict(std_references, new_references)
        #
        if not outcome:
            print("New references equal expected outcome: ", False)
            rubric["T19.01.01: credit references equal"]=False
            rubric["T19.01: confirmed"] = False
        else:
            print("New references equal expected outcome: ", True)
            rubric["T19.01.01: credit references equal"]=True
        #
        print("T19.01 finished. \n\n")
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
                print("API_Forecast passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("API_Forecast passed: ", True)
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
