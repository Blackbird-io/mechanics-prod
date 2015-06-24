#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Summarization.Grader

import copy
import dill
import sys
import traceback

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

def lineByLine(A,B):
    n = 0
    for aL,bL in zip(A,B):
        print(n)
        n = n + 1
        print("Line A: \n",aL)
        print("Line B: \n",bL)
        print(aL == bL)
        if aL == bL:
            continue
        else:
            for attr in aL.keyAttributes:
                print(attr)
                print("print(getattr(aL,attr))")
                print(getattr(aL,attr))
                print("print(getattr(bL,attr))")
                print(getattr(bL,attr))
                print("print(getattr(aL,attr) == getattr(bL,attr))")
                print(getattr(aL,attr) == getattr(bL,attr))
                print("\n")
            print("\n\n")

def check(result,standard):
    #standard is a stored version of the ``perfect`` output, w symmetrical
    #keys
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        c = ""
        c = """

        This test checks whether the summary of a model built from known inputs
        in the current build matches the summary of the known (intended) output
        of that model in a verified build.

        Grader will award an affirmative score ("pass") for all new summaries
        that include the entirety of information from known summaries.
        
        """
        print(c)
        o = result["output"]
        #16.01:
        print("T16.01: compare model summaries")
        rubric["T16.01: confirmed"] = True
        new_summary = o["T16.01"]["summary"]
        known_summary = standard["T16.01"]["summary"]
        print("""
        new_summary = o["T16.01"]["summary"]
        known_summary = standard["T16.01"]["summary"]
        """)
        print("new_summary: \n%s\n" % new_summary)
        print("known_summary: \n%s\n" % known_summary)
        #
        known_keys = sorted(known_summary.keys())
        #maintain fixed order of keys
        print("""
        known_keys = sorted(known_summary.keys())
        """)
        print("Known keys: \n", known_keys)
        c = """Iterate through known_keys, check that values in new summary
        match those in known summary. New summary may include additional
        data and still pass the test."""
        print(c)
        #
        outcome = True
        for (i,k) in enumerate(known_keys):
            known_value = known_summary[k]
            new_value = new_summary[k]
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
            print("new_summary is a superset of known_summary: ", False)
            rubric["T16.01.01: summaries match"]=False
            rubric["T16.01: confirmed"] = False
        else:
            print("new_summary is a superset of known_summary: ", True)
            rubric["T16.01.01: summaries match"]=True
        #
        print("T16.01 finished. \n\n")
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
                print("Summarization passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("Summarization passed: ", True)
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
