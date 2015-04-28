#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Model_01_Retail.Grader




#imports
import copy
import dill
import os
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
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        o = result["output"]
        #11.01:
        print("T11.01: compare modelling outcomes")
        rubric["T11.01: confirmed"] = True
        oM = o["T11.01"]["M"]
        #standard is a stored version of the ``perfect`` output, w symmetrical
        #keys
        sM = standard["T11.01"]["M"]
        o_topBU = oM.currentPeriod.content
        s_topBU = sM.currentPeriod.content
        o_fins = o_topBU.financials
        s_fins = s_topBU.financials
        print("""
        oM = o["T11.01"]["M"]
        sM = standard["T11.01"]["M"]
        o_topBU = oM.currentPeriod.content
        s_topBU = sM.currentPeriod.content
        o_fins = o_topBU.financials
        s_fins = s_topBU.financials
        """)
        print("o_fins: \n%s" % o_fins)
        print("s_fins: \n%s" % s_fins)
        if not o_fins == s_fins:
            print("o_fins == s_fins: ", False)
            rubric["T11.01.01: in-mem financials match"]=False
            rubric["T11.01: confirmed"] = False
            print("\n")
            print("""

            Details of mem-to-standard mismatch:

            A: o_fins
            B: s_fins
            """)
            lineByLine(o_fins,s_fins)
        else:
            print("o_fins == s_fins: ", True)
            rubric["T11.01.01: in-mem financials match"]=True
        #
        c = """

        The task for this test involves generating and **storing** the model.
        Make sure storage and recovery succeed without any errors. Note that
        new_model.pkl stores only the model, not a dictionary like ``output`` or
        standard.pkl.

        First, compare the serialized model to its in-memory representation to
        make sure saving and recovery keeps the object consistent.
        """
        print(c)
        p_store = r"tests\basic\model_01_retail\new_model.pkl"
        p_store = os.path.normpath(p_store)
        #make path portable
        #
        f = open(p_store,"rb")
        hardOM = dill.load(f)
        f.close()
        #
        print(r"""
        p_store = r"tests\basic\model_01_retail\new_model.pkl"
        f = open(p_store,"rb")
        hardOM = dill.load(f)
        f.close()
        """)
        hard_topBU = hardOM.currentPeriod.content
        hard_fins = hard_topBU.financials
        print("""
        hard_topBU = hardOM.currentPeriod.content
        hard_fins = hard_topBU.financials
        """)
        print("hard_fins: \n%s" % hard_fins)
        print("s_fins: \n%s" % o_fins)
        if not hard_fins == o_fins:
            print("hard_fins == o_fins: ", False)
            rubric["T11.01.02: file-to-mem financials match"]=False
            rubric["T11.01: confirmed"] = False
            print("\n")
            print("""

            Details of file-to-mem mismatch:

            A: hard_fins
            B: o_fins
            """)
            lineByLine(hard_fins,o_fins)         
        else:
            print("hard_fins == o_fins: ", True)
            rubric["T11.01.02: file-to-mem financials match"]=True
        print("""

        Second, check the recovered model against the standard.

        """)
        if not hard_fins == s_fins:
            print("hard_fins == s_fins: ", False)
            rubric["T11.01.03: serialized financials match"]=False
            rubric["T11.01: confirmed"] = False
            print("\n")
            print("""

            Details of serial-to-standard mismatch:

            A: hard_fins
            B: s_fins
            """)
            lineByLine(hard_fins,s_fins)         
        else:
            print("hard_fins == s_fins: ", True)
            rubric["T11.01.03: serialized financials match"]=True
        print("T11.01 finished. \n\n")
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
                print("Model_01_Retail passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("Model_01_Retail passed: ", True)
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
