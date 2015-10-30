#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Queue_01.Grader

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
        slate1 = standard["slate1"]
        slate2 = standard["slate2"]
        slate3 = standard["slate3"]
        slate4 = standard["slate4"]
        slate5 = standard["slate5"]
        slate6 = standard["slate6"]
        o_testQ = o["testQ"]
        s_testQ = standard["testQ"]
        #
        #
        #Task 4.01: conforming slate         
        print("T4.01: conforming slate")
        rubric["T4.01: confirmed"] = True
        print("default slate 1 order: \n")
        for i in slate1:
                print(i.name+", ")
        random.shuffle(slate1)
        print("random.shuffle(slate1)")
        print("shuffled slate 1 order: \n")
        for i in slate1:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate1)
        print("clear and extend testQs by slate1")
        oMisfits = o_testQ.alignItems()
        sMisfits = s_testQ.alignItems()
        print("oMisfits: %s\n" % oMisfits)
        print("sMisfits: %s\n" % sMisfits)
        print("o_testQ length: %s\n" % len(o_testQ))
        print("s_testQ length: %s\n" % len(s_testQ))
        print("slate1 length:  %s\n" % len(slate1))
        if not len(o_testQ) == len(s_testQ) == len(slate1):
            print("len(o_testQ) == len(s_testQ) == len(slate1): ", False)
            rubric["T4.01.01: conforming slate aligns"] = False
            rubric["T4.01: confirmed"] = False
        else:
            print("len(o_testQ) == len(s_testQ) == len(slate1): ", True)
            rubric["T4.01.01: conforming slate aligns"] = True
        del slate1
        print("T4.01 finished. \n\n")
        #
        #
        #Task 4.02: other firsts
        print("T4.02: other firsts")
        rubric["T4.02: confirmed"] = True
        print("default slate 2 order: \n")
        for i in slate2:
                print(i.name+", ")
        random.shuffle(slate2)
        print("random.shuffle(slate2)")
        print("shuffled slate 2 order: \n")
        for i in slate2:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate2)
        print("clear and extend testQs by slate2")
        oMisfits = o_testQ.alignItems()
        sMisfits = s_testQ.alignItems()
        print("o_testQ length: %s\n" % len(o_testQ))
        print("s_testQ length: %s\n" % len(s_testQ))
        print("slate2 length:  %s\n" % len(slate2))
        if not len(o_testQ) == len(s_testQ) == len(slate2)-2:
            print("len(o_testQ) == len(s_testQ) == len(slate1)-2: ", False)
            rubric["T4.02.01: excess first length matches"] = False
            rubric["T4.02: confirmed"] = False
        else:
            print("len(o_testQ) == len(s_testQ) == len(slate2)-2: ", True)
            rubric["T4.02.01: excess first length matches"] = True
        bktF = standard["bucketF"]
        print("""bktF = standard["bucketF"]""")
        print("oMisfits[0].name: %s" % oMisfits[0].name)
        print("oMName = oMisfits[0].name")
        t02 = True
        print("t02 = True")
        for i in bktF:
            if i.name == oMisfits[0].name:
                break
            else:
                continue
        else:
            t02 = False
        print("""
        for i in bktF:
            if i.name == oMisfits[0].name:
                break
            else:
                continue
        else:
            t02 = False
        """)
        if not t02:
            print("t02: ",False)
            rubric["T4.02.02: firsts misfit"] = False
            rubric["T4.02: confirmed"] = False
        else:
            print("t02: ",True)
            rubric["T4.02.02: firsts misfit"] = True
        del slate2
        print("T4.02 finished. \n\n")
        #
        #
        #Task 4.03: other lasts
        print("T4.03: other lasts")
        rubric["T4.03: confirmed"] = True
        print("default slate 3 order: \n")
        for i in slate3:
                print(i.name+", ")
        random.shuffle(slate3)
        print("random.shuffle(slate3)")
        print("shuffled slate 3 order: \n")
        for i in slate3:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate3)
        print("clear and extend testQs by slate3")
        oMisfits = o_testQ.alignItems()
        sMisfits = s_testQ.alignItems()
        print("o_testQ length: %s\n" % len(o_testQ))
        print("s_testQ length: %s\n" % len(s_testQ))
        print("slate3 length:  %s\n" % len(slate3))
        if not len(o_testQ) == len(s_testQ) == len(slate3)-2:
            print("len(o_testQ) == len(s_testQ) == len(slate3)-2: ", False)
            rubric["T4.03.01: excess last length matches"] = False
            rubric["T4.03: confirmed"] = False
        else:
            print("len(o_testQ) == len(s_testQ) == len(slate3)-2: ", True)
            rubric["T4.03.01: excess last length matches"] = True
        bktL = standard["bucketL"]
        print("""bktL = standard["bucketL"]""")
        print("oMisfits[0].name: %s" % oMisfits[0].name)
        t03 = True
        print("t03 = True")
        for i in bktL:
            if i.name == oMisfits[0].name:
                break
            else:
                continue
        else:
            t03 = False
        print("""
        for i in bktL:
            if i.name == oMisfits[0].name:
                break
            else:
                continue
        else:
            t03 = False
        """)
        if not t03:
            print("t03: ",False)
            rubric["T4.03.02: firsts misfit"] = False
            rubric["T4.03: confirmed"] = False
        else:
            print("t03: ",True)
            rubric["T4.03.02: firsts misfit"] = True
        del slate3
        print("T4.03 finished. \n\n")
        #
        #
        #Task 4.04: no firsts nonconforming
        print("T4.04: no firsts nonconforming")
        rubric["T4.04: confirmed"] = True
        print("default slate 4 order: \n")
        for i in slate4:
                print(i.name+", ")
        random.shuffle(slate4)
        print("random.shuffle(slate4)")
        print("shuffled slate 4 order: \n")
        for i in slate4:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate4)
        print("clear and extend testQs by slate4")
        oMisfits = o_testQ.alignItems()
        sMisfits = s_testQ.alignItems()
        print("o_testQ  length: %s\n" % len(o_testQ))
##      print("o_testQ[0].name: %s\n" % o_testQ[0].name)
##      print("o_testQ[0].canBeFirst: %s\n" % o_testQ[0].canBeFirst)
##      print("o_testQ[0].mustBeFirst: %s\n" % o_testQ[0].mustBeFirst)
        print("oMisfits length: %s\n" % len(oMisfits))
        print("s_testQ  length: %s\n" % len(s_testQ))
        print("sMisfits length: %s\n" % len(sMisfits))
        print("slate4   length: %s\n" % len(slate4))
        if not (len(o_testQ) == 0 and len(oMisfits) == len(slate4)):
            print("(len(o_testQ) == 0 and len(oMisfits) == len(slate4)): ", False)
            rubric["T4.04.01: conform queue requires first"] = False
            rubric["T4.04: confirmed"] = False
        else:
            print("(len(o_testQ) == 0 and len(oMisfits) == len(slate4)): ", True)
            rubric["T4.04.01: conform queue requires first"] = True
        del slate4
        print("T4.04 finished. \n\n")
        #
        #
        #Task 4.05: no lasts nonconforming
        print("T4.05: no lasts nonconforming")
        rubric["T4.05: confirmed"] = True
        print("default slate 5 order: \n")
        for i in slate5:
                print(i.name+", ")
        random.shuffle(slate5)
        print("random.shuffle(slate5)")
        print("shuffled slate 5 order: \n")
        for i in slate5:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate5)
        print("clear and extend testQs by slate5")
        oMisfits = o_testQ.alignItems()
        sMisfits = s_testQ.alignItems()
        print("o_testQ  length: %s\n" % len(o_testQ))
        print("oMisfits length: %s\n" % len(oMisfits))
        print("s_testQ  length: %s\n" % len(s_testQ))
        print("sMisfits length: %s\n" % len(sMisfits))
        print("slate4   length: %s\n" % len(slate5))
        if not (len(o_testQ) == 0 and len(oMisfits) == len(slate5)):
            print("len(o_testQ) == 0 and len(oMisfits) == len(slate5): ", False)
            rubric["T4.05.01: conform queue requires last"] = False
            rubric["T4.05: confirmed"] = False
        else:
            print("len(o_testQ) == 0 and len(oMisfits) == len(slate5): ", True)
            rubric["T4.05.01: conform queue requires last"] = True
        del slate5
        print("T4.05 finished. \n\n")
        #
        #
        #Task 4.06: conform w multitype misfits
        print("T4.06: conform w multitype misfits")
        rubric["T4.06: confirmed"] = True
        print("default slate 6 order: \n")
        for i in slate6:
                print(i.name+", ")
        random.shuffle(slate6)
        print("random.shuffle(slate6)")
        print("shuffled slate 6 order: \n")
        for i in slate6:
                print(i.name+", ")
        for Q in [o_testQ,s_testQ]:
                Q.clear()
                Q.extend(slate6)
        print("clear and extend testQs by slate6")
        oMisfits = o_testQ.alignItems()        
        print("o_testQ length: %s\n" % len(o_testQ))
        print("oMisfits length: %s\n" % len(oMisfits))
        print("slate6 length:  %s\n" % len(slate6))
        bktF = standard["bucketF"]
        print("""bktF = standard["bucketF"]""")
        bktL = standard["bucketL"]
        print("""bktL = standard["bucketL"]""")
        t06 = True
        print("t06 = True")
        oM_nameSet = set()
        for i in oMisfits:
            oM_nameSet.add(i.name)
        print("""
        oM_nameSet = set()
        for i in oMisfits:
            oM_nameSet.add(i.name)
        """)
        print("all oMisfits should come from either bktF or bktL")
        print("removing all bktF and bktL names should leave empty name set")
        nonconf = bktF + bktL
        print("nonconf = bktF+bktL")
        for i in nonconf:
            try:
                oM_nameSet.remove(i.name)
            except KeyError:
                continue
        print("""
        for i in nonconf:
            try:
                oM_nameSet.remove(i.name)
            except KeyError:
                continue
        """)
        if oM_nameSet != set(): t06 = False
        print("""if oM_nameSet != set(): t06 = False""")
        if not t06:
            print("t06: ",False)
            rubric["T4.06.01: correct misfit types"] = False
            rubric["T4.06: confirmed"] = False
        else:
            print("t06: ",True)
            rubric["T4.06.01: correct misfit types"] = True
        del slate6
        print("T4.06 finished. \n\n")
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
                print("Financials_01 passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("Queue_01 passed: ", True)
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
