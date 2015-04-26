#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\LifeCycle_01.Grader

import traceback
import copy
import sys

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
        output = result["output"]
        #Task 3.01: make and compare lifeStages
        print("T3.01: make and compare lifeStages")
        rubric["T3.01: confirmed"] = True
        o_stages_1 = output["T3.01"]["stages_1"]
        o_old = output["T3.01"]["old"]
        s_stages_1 = standard["T3.01"]["stages_1"]
        s_stages_2 = standard["T3.01"]["stages_2"]
        print("compare output and standard starting points")
        o_stages_1_view = ""
        s_stages_1_view = ""
        for o in o_stages_1: 
            o_stages_1_view += str(o)+"\n"
        for s in s_stages_1: 
            s_stages_1_view += str(s)+"\n"
        print("o_stages_1: \n", o_stages_1_view)
        print("s_stages_1: \n", s_stages_1_view)
        if not o_stages_1_view == s_stages_1_view:
            print("o_stages_1_view == s_stages_1_view: ", False)
            rubric["T3.01.01: starting points match"] = False
            rubric["T3.01: confirmed"] = False
        else:
            print("o_stages_1_view == s_stages_1_view: ", True)
            rubric["T3.01.01: starting points match"] = True
        o_stages_2 = o_stages_1
        o_old.makeLast()
        print("o_old.makeLast()")
        o_stages_2[2].ends = o_old.starts-1
        o_stages_2.append(o_old)
        o_stages_2_view = ""
        s_stages_2_view = ""
        for o,s in zip(o_stages_2,s_stages_2):
            o_stages_2_view += str(o)
            s_stages_2_view += str(s)
        print("o_stages_2: \n", o_stages_2_view)
        print("s_stages_2: \n", s_stages_2_view)
        if not o_stages_2_view == s_stages_2_view:
            print("o_stages_2_view == s_stages_2_view: ", False)
            rubric["T3.01.02: stage transforms match"] = False
            rubric["T3.01: confirmed"] = False
        else:
            print("o_stages_2_view == s_stages_2_view: ", True)
            rubric["T3.01.02: stage transforms match"] = True
        print("T3.01 finished. \n\n")
        #
        #
        #Task 3.02:
        print("T3.02: set lifestages")
        rubric["T3.02: confirmed"] = True
        o_lc1 = output["T3.02"]["lc1"]
        o_lc2 = output["T3.02"]["lc2"]
        o_lc3 = output["T3.02"]["lc3"]
        o_lc1.setLifeStages(o_stages_2)
        print("o_lc1.setLifeStages(o_stages_2)")
        o_lc2.allLifeStages = o_stages_2
        print("o_lc2.allLifeStages = o_stages_2")
        o_lc3.allLifeStages = o_stages_2
        print("o_lc3.allLifeStages = o_stages_2")
        for x in ["lc1","lc2","lc3"]:
            print("id(%s.allLifeStages)\t%s" %
                  (x,id(output["T3.02"][x].allLifeStages)))
        if not o_lc1.allLifeStages == o_lc2.allLifeStages == o_lc3.allLifeStages:
            print("o_lc1.allLifeStages == o_lc2.allLifeStages == o_lc3.allLifeStages: ", False)
            rubric["T3.02.01: lifestage substantive parity"] = False
            rubric["T3.02: confirmed"] = False     
        else:
            print("o_lc1.allLifeStages == o_lc2.allLifeStages == o_lc3.allLifeStages: ", True)
            rubric["T3.02.01: lifestage substantive parity"] = True
        if o_lc1.allLifeStages is o_lc2.allLifeStages:
            print("o_lc1.allLifeStages is o_lc2.allLifeStages: ", True)
            rubric["T3.02.02: set stages deepcopy works"] = False
            rubric["T3.02: confirmed"] = False
        else:
            print("o_lc1.allLifeStages is o_lc2.allLifeStages: ", False)
            rubric["T3.02.02: set stages deepcopy works"] = True
        if not o_lc2.allLifeStages is o_lc3.allLifeStages:
            print("o_lc2.allLifeStages is o_lc3.allLifeStages: ", False)
            rubric["T3.02.03: direct set identity"] = False
            rubric["T3.02: confirmed"] = False
        else:
            print("o_lc2.allLifeStages is o_lc3.allLifeStages: ", True)
            rubric["T3.02.03: direct set identity"] = True
        print("T3.02 finished. \n\n")
        #
        #
        #Task 3.03:
        print("T3.03: make and compare lifeCycles")
        rubric["T3.03: confirmed"] = True
        o_lc4 = output["T3.03"]["lc4"]
        o_lc5 = output["T3.03"]["lc5"]
        o_lc6 = output["T3.03"]["lc6"]
        o_lc7 = output["T3.03"]["lc7"]
        o_lc8 = output["T3.03"]["lc8"]
        o_batch_keys = ["lc4","lc5","lc6","lc7","lc8"]
        for k in o_batch_keys:
            print("\n")
            print(k)
            print("refDate:  ", output["T3.03"][k].refDate)
            print("dateBorn: ", output["T3.03"][k].dateBorn)
            print("age:      ", output["T3.03"][k].age)
            print("lifeSpan: ", output["T3.03"][k].lifeSpan)
            print("% done:   ", output["T3.03"][k].percentDone)
            print("alive:    ", output["T3.03"][k].alive)
            print("stg name: ", output["T3.03"][k].currentLifeStageName)
            print("stg num:  ", output["T3.03"][k].currentLifeStageNumber)
            print("+++++++++++")
        if not o_lc4.refDate == o_lc5.refDate:
            print("o_lc4.refDate == o_lc5.refDate: ", False)
            rubric["T3.03.01: batch ref dates match"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("o_lc4.refDate == o_lc5.refDate: ", True)
            rubric["T3.03.01: batch ref dates match"] = True
        if not o_lc5.age == o_lc6.age:
            print("o_lc5.age == o_lc6.age: ", False)
            rubric["T3.03.02: age spec match"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("o_lc5.age == o_lc6.age: ", True)
            rubric["T3.03.02: age spec match"] = True
        if not o_lc6.dateBorn == o_lc7.dateBorn:
            print("o_lc6.dateBorn == o_lc7.dateBorn: ", False)
            rubric["T3.03.03: date born calc works"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("o_lc6.dateBorn == o_lc7.dateBorn: ", True)
            rubric["T3.03.03: date born calc works"] = True
        o_batch = [o_lc4,o_lc5,o_lc6,o_lc7,o_lc8]
        s_lc4 = standard["T3.03"]["lc4"]
        s_lc5 = standard["T3.03"]["lc5"]
        s_lc6 = standard["T3.03"]["lc6"]
        s_lc7 = standard["T3.03"]["lc7"]
        s_lc8 = standard["T3.03"]["lc8"]
        s_batch = [s_lc4,s_lc5,s_lc6,s_lc7,s_lc8]
        if not o_batch == s_batch:
            print("o_batch == s_batch: ", False)
            rubric["T3.03.04: lifecycle batches match"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("o_batch == s_batch: ", True)
            rubric["T3.03.04: lifecycle batches match"] = True
        o_lc8_1 = copy.deepcopy(o_lc8)
        o_lc8_2 = copy.deepcopy(o_lc8)
        o_lc8_3 = copy.deepcopy(o_lc8)
        o_lc8_4 = copy.deepcopy(o_lc8)
        o_lc8_5 = copy.deepcopy(o_lc8)
        incrementA = 60*60*24*30*12*2
        print("incrementA = 60*60*24*30*12*2")
        incrementB = 60*60*24*30*12*0.5
        print("incrementB = 60*60*24*30*12*0.5")
        o_lc8_1.makeYounger(incrementB)
        print("o_lc8_1.age: ", o_lc8_1.age)
        print("o_lc8_1.makeYounger(incrementB)")
        o_lc8_2.moveBackwardInTime(incrementB)
        print("o_lc8_2.moveBackwardInTime(incrementB)")
        print("o_lc8_2.age: ", o_lc8_2.age)
        for x in range(6):
            o_lc8_3.moveBackwardInTime()
            #use standard denomination here
        print("move o_lc8_3 back in time 5 times w std increment")
        print("o_lc8_3.age: ", o_lc8_3.age)
        if not o_lc8_1.age == o_lc8_2.age == o_lc8_3.age:
            print("o_lc8_1.age == o_lc8_2.age == o_lc8_3.age: ", False)
            rubric["T3.03.05: rear parity for age/refDate"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("o_lc8_1.age == o_lc8_2.age == o_lc8_3.age: ", True)
            rubric["T3.03.05: rear parity for age/refDate"] = True
        o_lc8_4.makeOlder(incrementA)
        print("o_lc8_4.makeOlder(incrementA)")
        print("o_lc8_4.refDate: ", o_lc8_4.refDate)
        print("o_lc8_4.age: ", o_lc8_4.age)
        print("o_lc8_4.percentDone: ", o_lc8_4.percentDone)
        print("o_lc8_4.currentLifeStageName: ", o_lc8_4.currentLifeStageName)
        o_lc8_5.moveForwardInTime(incrementA)
        print("o_lc8_5.moveForwardInTime(incrementA)")
        print("o_lc8_5.refDate: ", o_lc8_5.refDate)
        print("o_lc8_5.age: ", o_lc8_5.age)
        print("o_lc8_5.percentDone: ", o_lc8_5.percentDone)
        print("o_lc8_5.currentLifeStageName: ", o_lc8_5.currentLifeStageName)
        s_lc8_4 = standard["T3.03"]["lc8_4"]
        s_lc8_5 = standard["T3.03"]["lc8_5"]
        #compare to standards here
        o_fwd = [o_lc8_4,o_lc8_5]
        print("o_fwd = [o_lc8_4,o_lc8_5]")
        s_fwd = [s_lc8_4,s_lc8_5]
        print("s_fwd = [s_lc8_4,s_lc8_5]")
        if not o_fwd == s_fwd:
            print("if not o_fwd == s_fwd: ", False)
            rubric["T3.03.06: fwd parity for age/refDate"] = False
            rubric["T3.03: confirmed"] = False
        else:
            print("if not o_fwd == s_fwd: ", True)
            rubric["T3.03.06: fwd parity for age/refDate"] = True
        print("T3.03 finished. \n\n")
        #
        #
        #Task 3.04:
        print("T3.04: linked lifeStage pointers")
        rubric["T3.04: confirmed"] = True
        s_stages_2 = standard["T3.04"]["stages_2"]
        s_stages_3 = standard["T3.04"]["stages_3"]
        o_slate = output["T3.04"]["slate"]
        s_slate_1 = standard["T3.04"]["slate_1"]
        s_slate_2 = standard["T3.04"]["slate_2"]
        def showSlate(slate):
            res = ""
            for i in range(len(slate)):
                res += "\n"
                res += ("Object %s\n" % i)
                res += ("refDate:  %s\n" % slate[i].refDate)
                res += ("dateBorn: %s\n" % slate[i].dateBorn)
                res += ("age:      %s\n" % slate[i].age)
                res += ("lifeSpan: %s\n" % slate[i].lifeSpan)
                res += ("pct done: %s\n" % slate[i].percentDone)
                res += ("alive:    %s\n" % slate[i].alive)
                res += ("stg name: %s\n" % slate[i].currentLifeStageName)
                res += ("stg num:  %s\n" % slate[i].currentLifeStageNumber)
                res += ("+++++++++++\n")
            res += ("+++++++++++++++\n")
            return res
        for i in o_slate:
            i.allLifeStages = s_stages_2
        print("manually set i.allLifeStages to ``s_stages_2`` in o_slate")
        print("all objects in slate now reference same life objects")
        o_slate_view1 = showSlate(o_slate)
        print("o_slate_view1 = showSlate(o_slate)")
        print(o_slate_view1)
        s_slate_view1 = showSlate(s_slate_1)
        print("s_slate_view1 = showSlate(s_slate_1)")
        print(s_slate_view1)
        if not o_slate_view1 == s_slate_view1:
            print("o_slate_view1 == s_slate_view1: ", False)
            rubric["T3.04.01: linked stages start match"] = False
            rubric["T3.04: confirmed"] = False
        else:
            print("o_slate_view1 == s_slate_view1: ", True)
            rubric["T3.04.01: linked stages start match"] = True
        for i in o_slate:
            i.allLifeStages = s_stages_3
        print("manually set i.allLifeStages to ``s_stages_3`` in o_slate")
        print("all objects in slate now reference same life stage objects")
        o_slate_view2 = showSlate(o_slate)
        print("o_slate_view2 = showSlate(o_slate)")
        print(o_slate_view2)
        s_slate_view2 = showSlate(s_slate_2)
        print("s_slate_view2 = showSlate(s_slate_2)")
        print(s_slate_view2)
        if not o_slate_view2 == s_slate_view2:
            print("o_slate_view2 == s_slate_view2: ", False)
            rubric["T3.04.02: linked stages end match"] = False
            rubric["T3.04: confirmed"] = False
        else:
            print("o_slate_view2 == s_slate_view2: ", True)
            rubric["T3.04.02: linked stages end match"] = True
        print("T3.04 finished. \n\n")
        #
        #
        #check rubric, figure out result
        #this test reqiures 100% accuracy, so decision criterion is simple
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
            print("LifeCycle_01 passed: ", True)
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
