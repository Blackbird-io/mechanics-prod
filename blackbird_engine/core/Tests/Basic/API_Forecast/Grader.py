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
        known_keys = sorted(std_references.keys())
        #maintain fixed order of keys
        print("""
        known_keys = sorted(std_references.keys())
        """)
        print("Known keys: \n", known_keys)
        c = """

        Iterate through known_keys, check that references for each request
        match expected data. 

        Test requires 100% match for each known credit reference to pass. 
        """
        print(c)
        #
        outcome = True
        for (i,k) in enumerate(known_keys):
            known_value = std_references[k]
            new_value = new_references[k]
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
