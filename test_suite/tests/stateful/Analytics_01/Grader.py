#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Analytics_01.Grader

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

def check(result,standard):
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        o = result["output"]
        #12.01:
        print("T12.01: compare analytics output")
        rubric["T12.01: confirmed"] = True       
        #standard contains ``perfect`` output, w symmetrical keys
        oM = o["T12.01"]["uM"]
        sM = standard["T12.01"]["uM"]
        o_atx = oM.analytics
        s_atx = sM.analytics
        o_l_sum = o["T12.02"]["l_sum"]
        s_l_sum = standard["T12.02"]["l_sum"]
        print("""
        oM = o["T12.01"]["uM"]
        sM = standard["T12.01"]["uM"]
        o_atx = oM.analytics
        s_atx = sM.analytics
        o_l_sum = o["T12.02"]["l_sum"]
        s_l_sum = standard["T12.02"]["l_sum"]
        """)
        #12.01:
        c = """

        Start by comparing the analytics objects themselves.
        
        Since analytics as a whole are unwieldy to view, go to straight to
        logical comparison.
        
        """
        print(c)
        if not o_atx == s_atx:
            print("o_atx == s_atx: ", False)
            rubric["T12.01.01: analytics objects match completely"]=False
            rubric["T12.01: confirmed"] = False
        else:
            print("o_atx == s_atx: ", True)
            rubric["T12.01.01: analytics objects match completely"]=True
        #
        print("T12.01 finished. \n\n")
        #
        #12.02
        print("T12.02: compare summaries")
        rubric["T12.02: confirmed"] = True
        c = """

        Now, compare landscape summaries. For identical models and market color,
        these should match exactly.
        
        """
        print(c)
        print("output landscape summary:   \n", o_l_sum)
        print("standard landscape summary: \n", s_l_sum)
        if not o_l_sum == s_l_sum:
            print("o_l_sum == s_l_sum: ", False)
            rubric["T12.02.01: landscape summaries match"]=False
            rubric["T12.02: confirmed"] = False
        else:
            print("o_l_sum == s_l_sum: ", True)
            rubric["T12.02.01: landscape summaries match"]=True
        print("T12.02 finished. \n\n")
        #
        #12.03
        print("T12.03: compare references")
        rubric["T12.03: confirmed"] = True
        c = """

        Now, compare references for specific price points. These should also
        match exactly.
        
        """
        print(c)
        ref_keys = sorted(standard["T12.03"].keys())
        c = """
        ref_keys = sorted(standard["T12.03"].keys())
        """
        print("ref_keys: \n", ref_keys)
        print("\n\n")
        print("output references:")
        #use repr to print individual references because they still run on
        #lineItem print logic, which shows their .value attribute (None)
        for k in ref_keys:
            print("\n")
            print(k)
            o_ref = o["T12.03"][k]
            print(repr(o_ref))
        print("\n\n")
        print("standard references:")
        for k in ref_keys:
            print("\n")
            print(k)
            s_ref = standard["T12.03"][k]
            print(repr(s_ref))
        o_refs = o["T12.03"]
        s_refs = standard["T12.03"]
        c = """
        o_refs = o["T12.03"]
        s_refs = standard["T12.03"]
        """
        print(c)
        if not o_refs == s_refs:
            print("o_refs == s_refs: ", False)
            rubric["T12.03.01: credit references match"]=False
            rubric["T12.03: confirmed"] = False
        else:
            print("o_refs == s_refs: ", True)
            rubric["T12.03.01: credit references match"]=True
        print("T12.03 finished. \n\n")
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
                print("Analytics_01 passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("Analytics_01 passed: ", True)
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
