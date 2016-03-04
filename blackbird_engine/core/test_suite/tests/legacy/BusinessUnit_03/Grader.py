#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BusinessUnit_03.Grader

import traceback
import copy
import sys
import random

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
        #6.03:
        print("T6.03: check consolidation functions")
        rubric["T6.03: confirmed"] = True
        oA3 = o["T6.03"]["A3"]
        sA3_1 = standard["T6.03"]["A3_1"]
        sA3_2 = standard["T6.03"]["A3_2"]
        sA3_3 = standard["T6.03"]["A3_3"]
        oA3_1 = copy.deepcopy(oA3)
        oA3_2 = copy.deepcopy(oA3)
        oA3_3 = copy.deepcopy(oA3)
        print("""
        oA3 = o["T6.03"]["A3"]
        sA3_1 = standard["T6.03"]["A3_1"]
        sA3_2 = standard["T6.03"]["A3_2"]
        sA3_3 = standard["T6.03"]["A3_3"]
        oA3_1 = copy.deepcopy(oA3)
        oA3_2 = copy.deepcopy(oA3)
        oA3_3 = copy.deepcopy(oA3)
        """)
        print("oA3_1.financials: \n%s" % oA3_1.financials)
        print("sA3_1.financials: \n%s" % sA3_1.financials)
        if not oA3_1 == sA3_1:
            print("oA3_1 == sA3_1: ", False)
            rubric["T6.03.01: starting points match"]=False
            rubric["T6.03: confirmed"] = False
        else:
            print("oA3_1 == sA3_1: ", True)
            rubric["T6.03.01: starting points match"]=True
        oA3_2.consolidate()
        print("oA3_2.consolidate()")
        print("oA3_2.financials: \n%s" % oA3_2.financials)
        print("sA3_2.financials: \n%s" % sA3_2.financials)
        if not oA3_2 == sA3_2:
            print("oA3_2 == sA3_2: ", False)
            rubric["T6.03.02: consolidate results match"] = False
            rubric["T6.03: confirmed"] = False
        else:
            print("oA3_2 == sA3_2: ", True)
            rubric["T6.03.02: consolidate results match"] = True
        oA3_3.filled = False
        oA3_3.fillOut()
        print("oA3_3.fillOut()")
        print("oA3_3.financials: \n%s" % oA3_3.financials)
        if not oA3_3 == sA3_3:
            print("oA3_3 == sA3_3: ", False)
            rubric["T6.03.03: fillOut results match"] = False
            rubric["T6.03: confirmed"] = False
        else:
            print("oA3_3 == sA3_3: ", True)
            rubric["T6.03.03: fillOut results match"] = True
        print("Run fillOut() again, should be no-op/no-change")
        oA3_3.fillOut()
        print("oA3_3.fillOut()")
        if not oA3_3 == sA3_3:
            print("oA3_3 == sA3_3: ", False)
            rubric["T6.03.04: fillOut() repeat no-op"] = False
            rubric["T6.03: confirmed"] = False
        else:
            print("oA3_3 == sA3_3: ", True)
            rubric["T6.03.04: fillOut() repeat no-op"] = True
        print("T6.03 finished. \n\n")
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
                print("BusinessUnit_03 passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("BusinessUnit_03 passed: ", True)
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
