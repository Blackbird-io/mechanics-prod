#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Financials_01.Grader

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
        #Task 1.01: BookMarks
        print("T1.01: check basic bookmark properties")
        o_bmark1 = result["output"]["bmark1"]
        o_bmark2 = result["output"]["bmark2"]
        o_bmark3 = result["output"]["bmark3"]
        s_bmark1 = standard["bmark1"]
        s_bmark2 = standard["bmark2"]
        s_bmark3 = standard["bmark3"]
        print("comparing bookmarks to standard")
        marks = [(o_bmark1,s_bmark1),(o_bmark2,s_bmark2),(o_bmark3,s_bmark3)]
        for (x,y) in marks:
            print("output bookmark: \n",x)
            print("standard bookmark: \n",y)
            if not x == y:
                rubric["T1.01.01: bookmarks are equal"] = False
                rubric["T1.01: confirmed"] = False
                print("Task 1.01 (Bookmarks) failed equality")
            if not x.name == y.name:
                rubric["T1.01.02: bookmarks match names"] = False
                rubric["T1.01: confirmed"] = False
                print("Task 1.01 (Bookmarks) failed names")
            if not x.allTags == y.allTags:
                rubric["T1.01.03: bookmarks match tags"] = False
                rubric["T1.01: confirmed"] = False
                print("Task 1.01 (Bookmarks) failed tags")
        else:
            rubric["T1.01.01: bookmarks are equal"] = True
            rubric["T1.01.02: bookmarks match names"] = True
            rubric["T1.01.03: bookmarks match tags"] = True
            rubric["T1.01: confirmed"] = True
            print("Task 1.01 (Bookmarks) confirmed")
        print("T1.01 finished. \n\n")
        ##
        ##
        #Task 1.02: Basic Financials Objects
        print("T1.02: check that build produces equal default fin objects")
        o_fin1 = output["fin1"]
        o_fin2 = output["fin2"]
        o_fin3 = output["fin3"]
        o_fin4 = output["fin4"]
        print("fin1 and fin2 should be identical within output")
        print("o_fin1: \n",o_fin1)
        print("o_fin2: \n",o_fin2)
        if not o_fin1 == o_fin2:
            print("fin1 == fin2 \n", False)
            rubric["T1.02.01: bare fins equal"] = False
            rubric["T1.02: confirmed"] = False
        else:
            print("fin1 == fin2 \n", True)
            rubric["T1.02.01: bare fins equal"] = True
        print("T1.02 finished. \n\n")
        ##
        ##
        #Task 1.03: Top Level Names
        print("T1.03: check default settings for topLevelNames")
        rubric["T1.03: confirmed"] = True
        s_fin1 = standard["fin1"]
        s_fin2 = standard["fin2"]
        s_fin3 = standard["fin3"]
        s_fin4 = standard["fin4"]
        print("check default top level names")
        print("o_fin1.topLevelNames: \n",o_fin1.topLevelNames)
        print("s_fin1.topLevelNames: \n",s_fin1.topLevelNames)
        print("tLN should match for all output fins (all default)")
        if not (o_fin1.topLevelNames==o_fin2.topLevelNames==
                o_fin3.topLevelNames==o_fin4.topLevelNames):
            print("tLN for all output fins do not match")
            rubric["T1.03.01: identical default tLN in output"] = False
            rubric["T1.03: confirmed"] = False
        else:
            rubric["T1.03.01: identical default tLN in output"] = True
        print("tLN for o_fin1 should match s_fin1")
        if not o_fin1.topLevelNames == s_fin1.topLevelNames:
            print("o_fin1.topLevelNames == s_fin1.topLevelNames:\n",False)
            rubric["T1.03.02: standard default tLN"] = False
            rubric["T1.03: confirmed"] = False
        else:
            rubric["T1.03.02: standard default tLN"] = True
            print("o_fin1.topLevelNames == s_fin1.topLevelNames:\n",True)
        print("T1.03 finished. \n\n")
        ##
        ##
        #Task 1.04: hierarchy maps and groups for simple fins
        print("T1.04: check hierarchy maps and groups for simple fins")
        rubric["T1.04: confirmed"] = True
        print("calling .buildHierarchyMap for o_fin1")
        o_fin1.buildHierarchyMap()
        print("o_fin1.hierarchyMap: \n",o_fin1.hierarchyMap)
        print("calling .buildHierarchyMap for s_fin1")
        s_fin1.buildHierarchyMap()
        print("s_fin1.hierarchyMap: \n",s_fin1.hierarchyMap)
        print("compare o_fin1.hMap to standard")
        if not o_fin1.hierarchyMap == s_fin1.hierarchyMap:
            print("o_fin1.hierarchyMap == s_fin1.hierarchyMap",False)
            rubric["T1.04.01: simple fin hMap matches standard"] = False
            rubric["T1.04: confirmed"] = False
        else:
            print("o_fin1.hierarchyMap == s_fin1.hierarchyMap",True)
            rubric["T1.04.01: simple fin hMap matches standard"] = True
        print("compare o_fin1.hGroups to standard")
        print("(groups generated automatically when building hMap")
        if not o_fin1.hierarchyGroups == s_fin1.hierarchyGroups:
            print("o_fin1.hierarchyGroups == s_fin1.hierarchyGroups",False)
            rubric["T1.04.02: simple fin hGroups match standard"] = False
            rubric["T1.04: confirmed"] = False
        else:
            print("o_fin1.hierarchyGroups == s_fin1.hierarchyGroups",True)
            rubric["T1.04.02: simple fin hGroups match standard"] = True
        print("T1.04 finished. \n\n")
        ##
        ##  
        #Task 1.05: hMaps and hGroups for complex fins
        print("T1.05: check hierarchy maps and groups for complex fins")
        print("(i.e., fins w multiple levels of hierarchy")
        rubric["T1.05: confirmed"] = True
        print("calling .buildHierarchyMap for o_fin3")
        o_fin3.buildHierarchyMap()
        print("o_fin3.hierarchyMap: \n",o_fin1.hierarchyMap)
        print("calling .buildHierarchyMap for s_fin3")
        s_fin3.buildHierarchyMap()
        print("s_fin3.hierarchyMap: \n",s_fin3.hierarchyMap)
        print("compare hMap for ofin3 and standard")
        if not o_fin1.hierarchyMap == s_fin1.hierarchyMap:
            print("o_fin3.hierarchyMap == s_fin3.hierarchyMap",False)
            rubric["T1.05.01: complex fin hMap matches standard"] = False
            rubric["T1.05: confirmed"] = False
        else:
            print("o_fin3.hierarchyMap == s_fin3.hierarchyMap",True)
            rubric["T1.05.01: complex fin hMap matches standard"] = True
        print("compare o_fin3.hGroups to standard")
        print("(groups generated automatically when building hMap")
        if not o_fin3.hierarchyGroups == s_fin3.hierarchyGroups:
            print("o_fin3.hierarchyGroups == s_fin3.hierarchyGroups",False)
            rubric["T1.05.02: complex fin hGroups match standard"] = False
            rubric["T1.05: confirmed"] = False
        else:
            print("o_fin3.hierarchyGroups == s_fin3.hierarchyGroups",True)
            rubric["T1.05.02: complex fin hGroups match standard"] = True       
        print("T1.05 finished. \n\n")
        #
        #
        #Task 1.06: hGroups for fins w misfits
        print("T1.06: check hierarchy maps and groups for fins w misfits")
        rubric["T1.06: confirmed"] = True
        o_sharks = output["sharks"]
        print("``sharks`` is a lineitem that looks like a misfit in normal fins")
        print("sharks: \n",o_sharks)
        print("sharks.partOf: \n", o_sharks.partOf)
        print("``sharks`` should be in both o_fin4 and s_fin4")
        print("check that ``sharks`` is present in both")
        if o_sharks not in o_fin4:
            print("``sharks in o_fin4: ", False)
            rubric["T1.06.01: misfit included"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("``sharks in o_fin4: ", True)
            rubric["T1.06.01: misfit included"] = True
        if o_sharks not in s_fin4:
            print("``sharks in s_fin4: ", False)
            rubric["T1.06.02: misfit standard"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("``sharks in s_fin4: ", True)
            rubric["T1.06.02: misfit standard"] = True
        print("build & comparee hierarchy groups for o_fin4 and s_fin4")
        o_hg4 = o_fin4.buildHierarchyGroups()
        s_hg4 = s_fin4.buildHierarchyGroups()
        if not o_hg4 == s_hg4:
            print("o_hg4 == s_hg4: ",False)
            rubric["T1.06.03: h groups match"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("o_hg4 == s_hg4: ",True)
            rubric["T1.06.03: h groups match"] = True
        print("second item in .buildHierarchyMaps() should be list of misfits")
        if not o_hg4[1] == [o_sharks]:
            print("o_hg4[1] == [sharks]: ", False)
            rubric["T1.06.04: misfit group matches"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("o_hg4[1] == [sharks]: ", True)
            rubric["T1.06.04: misfit group matches"] = True
        o_fin4.buildHierarchyMap()
        s_fin4.buildHierarchyMap()
        print("check that hierarchy maps match for output and standard")
        print("o_fin4.hierarchyMap: \n",o_fin4.hierarchyMap)
        print("s_fin4.hierarchyMap: \n",s_fin4.hierarchyMap)
        if not o_fin4.hierarchyMap == s_fin4.hierarchyMap:
            print("o_fin4.hierarchyMap == s_fin4.hierarchyMap: ", False)
            rubric["T1.06.05: h maps match"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("o_fin4.hierarchyMap == s_fin4.hierarchyMap: ", True)
            rubric["T1.06.05: h maps match"] = True
        #
        print("get index of misfit label for each hmap")
        #
        try:
            o_mloc = o_fin4.hierarchyMap.index(o_fin4.misfitLabel)
            s_mloc = s_fin4.hierarchyMap.index(s_fin4.misfitLabel)
        except ValueError:
            rubric["T1.06.06: misfit label located"] = False
            rubric["T1.06: confirmed"] = False
        print("misfit label in o_fin4, s_fin4 at index: %s,%s" % (o_mloc,
                                                                  s_mloc))
        #
        if not o_mloc == s_mloc:
            print("o_mloc == s_mloc: ", False)
            rubric["T1.06.07: misfit index matches"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("o_mloc == s_mloc: ", True)
            rubric["T1.06.07: misfit index matches"] = True
        print("append ``Navy Seals`` to o_fin4.topLevelNames")
        print("this should resolve misfit status for ``shark``")
        o_fin4.topLevelNames.append(o_sharks.partOf)
        o_fin4.buildHierarchyMap()
        print("o_sharks.partOf: \n", o_sharks.partOf)
        print("o_fin4.topLevelNames: \n", o_fin4.topLevelNames)
        print("o_fin4.hierarchyMap: \n", o_fin4.hierarchyMap)
        if s_fin4.misfitLabel in o_fin4.hierarchyMap:
            print("misfitLabel not in o_fin4.hierarchyMap: ", False)
            rubric["T1.06.08: tLN adjustment works"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("misfitLabel not in o_fin4.hierarchyMap: ", True)
            rubric["T1.06.08: tLN adjustment works"] = True
        print("remove ``Navy Seals`` from tLN; check that misfit status reverts")
        o_fin4.topLevelNames.remove("Navy Seals")
        o_fin4.buildHierarchyMap()
        print("o_sharks.partOf: \n", o_sharks.partOf)
        print("o_fin4.topLevelNames: \n", o_fin4.topLevelNames)
        print("o_fin4.hierarchyMap: \n", o_fin4.hierarchyMap)
        if not s_fin4.misfitLabel in o_fin4.hierarchyMap:
            print("misfitLabel back in o_fin4.hierarchyMap: ", False)
            rubric["T1.06.09: tLN reversion works"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("misfitLabel back in o_fin4.hierarchyMap: ", True)
            rubric["T1.06.09: tLN reversion works"] = True
        print("change misfit label and make sure string in hmap changes too")
        o_fin4.setMisfitLabel("Outlier")
        o_fin4.buildHierarchyMap()
        print("o_fin4.hierarchyMap: \n", o_fin4.hierarchyMap)
        if not o_fin4.hierarchyMap[o_mloc] == "Outlier":
            print("misfit label toggles: ", False)
            rubric["T1.06.10: misfit label toggles"] = False
            rubric["T1.06: confirmed"] = False
        else:
            print("misfit label toggles: ", True)
            rubric["T1.06.10: misfit label toggles"] = True
        print("T1.06 finished. \n\n")
        #
        #
        #Task 1.07: hGroups for misordered fins: skip for now
        #
        #
        #Task 1.08: inserting summary lineitems 
        print("T1.08: confirm manage_summaries() inserts correct lineitems")
        rubric["T1.08: confirmed"] = True
        s_fin5_1 = standard["T1.08"]["fin5_1"]
        s_fin5_2 = standard["T1.08"]["fin5_2"]
        o_fin5 = output["T1.08"]["fin5"]
        print("o_fin5.autoSummarize: ", o_fin5.autoSummarize)
        print("s_fin5_1.autoSummarize: ", s_fin5_1.autoSummarize)
        o_fin5.buildHierarchyMap()
        o_fin5_str = str(o_fin5)
        s_fin5_1_str = str(s_fin5_1)
        if not o_fin5_str == s_fin5_1_str:
            print("o_fin5_str == s_fin5_1_str: ", False)
            print("starting fin print doesn't match standard")
            rubric["T1.08.01: complex fin views match"] = False
            rubric["T1.08: confirmed"] = False
        else:
            print("starting fin print matches standard")
            rubric["T1.08.01: complex fin views match"] = True
        print("run manage_summaries() on o_fin5, check if it matches s_fin5_2")
        o_fin5.manage_summaries()
        o_fin5_str2 = str(o_fin5)
        if not o_fin5_str2 == str(s_fin5_2):
            print("o_fin5_str2 == str(s_fin5_2): ", False)
            rubric["T1.08.02: summaries views match"] = False
            rubric["T1.08: confirmed"] = False
        else:
            print("o_fin5_str2 == str(s_fin5_2): ", True)
            rubric["T1.08.02: summaries views match"] = True
        print("T1.08 finished. \n\n")
        #
        #
        #Task 1.09: drop down replicas 
        print("T1.09: confirm replica insertion and incrementation")
        rubric["T1.09: confirmed"] = True
        o_fin6 = output["T1.09"]["fin6"]
        o_fin6_1 = copy.deepcopy(o_fin6)
        #save state before running behaviors
        o_fin6.manage_summaries()
        o_fin6.manageDropDownReplicas()
        o_fin6_str = str(o_fin6)
        s_fin6_1 = standard["T1.09"]["fin6_1"]
        s_fin6_2 = standard["T1.09"]["fin6_2"]
        s_fin6_3 = standard["T1.09"]["fin6_3"]
        print("check if replicas inserted correctly on first pass over complex fins")
        if not o_fin6_str == str(s_fin6_2):
            print("o_fin6_str == str(s_fin6_2): ", False)
            rubric["T1.09.01: replicas inserted correctly"] = False
            rubric["T1.09: confirmed"] = False
        else:
            print("o_fin6_str == str(s_fin6_2): ", True)
            rubric["T1.09.01: replicas inserted correctly"] = True
        topLoc = []
        s_fin6_1.buildHierarchyMap()
        for i in range(len(s_fin6_1)):
            if i <= len(s_fin6_1)-2:
                n0 = s_fin6_1.hierarchyMap[i]
                n1 = s_fin6_1.hierarchyMap[i+1]
                if n1 > n0:
                    topLoc.append(n0)
        ddrLoc = []
        s_fin6_2.buildHierarchyMap()
        for i in range(len(s_fin6_2)):
            if i <= len(s_fin6_2)-2:
                n0 = s_fin6_2.hierarchyMap[i]
                n1 = s_fin6_2.hierarchyMap[i+1]
                if n1 > n0:
                    ddrLoc.append((i,i+1))
        print("check that the replicas pulled down values from the reference top")
        rubric["T1.09.02: ddr pulls down starting value"] = True
        for i in range(len(topLoc)):
            topL = o_fin6_1[i]
            wDDR = ddrLoc[i]
            newTopL = o_fin6[wDDR[0]]
            ddrL = o_fin6[wDDR[1]]
            # topL.value must equal DDR[1]; DDR[0] must be None
            if not newTopL.value == None and ddrL.value == topL.value:
                print("original lineitem: \n",topL)
                print("top and ddr: \n%s\n%s" % (newTopL,ddrL))
                print("original and ddr do not match")
                rubric["T1.09.02: ddr pulls down starting value"] = False
                rubric["T1.09: confirmed"] = False
        #MAKE OBJ
        print("increment every top item in o_fin6 by a preset value; check that")
        print("ddr pulls it down")
        ddrUps = standard["T1.09"]["ddrUps"]
        o_fin6_1 = copy.deepcopy(o_fin6)
        for i in range(len(ddrLoc)):
            n0, n1 = ddrLoc[i]
            top = o_fin6[n0]
            top.setValue(ddrUps[i],"fin1_grader")
        print("run o_fin6.manageDropDownReplicas()")
        o_fin6.manageDropDownReplicas()
        o_fin6str = str(o_fin6)
        print("compare post-increment view to standard")
        print("\no_fin6: \n", o_fin6)
        print("\ns_fin6_3: \n",s_fin6_3)
        if not o_fin6str == str(s_fin6_3):
            print("o_fin6str == str(s_fin6_3): ", False)
            rubric["T1.09.03: ddr pulls down incremental value"] = False
            rubric["T1.09: confirmed"] = False
        else:
            print("o_fin6str == str(s_fin6_3): ", True)
            rubric["T1.09.02: ddr pulls down incremental value"] = True
        #
        #alternatively, could do a detailed check of each top and ddr pair by
        #walking through items indexed in ddrLoc. print view should, however,
        #accomplish the same thing faster.     
        print("T1.09 finished. \n\n")
        #
        #
        #Task 1.10: incrementing summary lineitems
        print("T1.10: check that summaries increment correctly")
        rubric["T1.10: confirmed"] = True
        s_fin7_1 = standard["T1.10"]["fin7_1"]
        s_fin7_2 = standard["T1.10"]["fin7_2"]
        s_fin7_3 = standard["T1.10"]["fin7_3"]
        newLs = standard["T1.10"]["newLs"]
        o_fin7 = output["T1.10"]["fin7"]
        o_fin7_1 = copy.deepcopy(o_fin7)
        print("starting point for output and standard financials")
        print("o_fin7_1: \n", o_fin7_1)
        print("s_fin7_2: \n", s_fin7_2)
        print("check starting point equality")
        if not str(o_fin7_1) == str(s_fin7_1):
            print("str(o_fin7_1) == str(s_fin7_1): ",False)
            rubric["T1.10.01: starting points match"] = False
            rubric["T1.10: confirmed"] = False
        else:
            print("str(o_fin7_1) == str(s_fin7_1): ",True)
            rubric["T1.10.01: starting points match"] = True
        o_fin7.manage_summaries()
        o_fin7.manageDropDownReplicas()
        o_fin7.updateSummaries()
        print("manage summaries, manage ddr, update summaries")
        print("compare stage 2")
        o_fin7_2 = copy.deepcopy(o_fin7)
        print("o_fin7_2: \n", o_fin7_2)
        print("s_fin7_2: \n", s_fin7_2)
        if not str(o_fin7_2) == str(s_fin7_2):
            print("str(o_fin7_2) == str(s_fin7_2): ", False)
            rubric["T1.10.02: first pass summaries match"] = False
            rubric["T1.10: confirmed"] = False
        else:
            print("str(o_fin7_2) == str(s_fin7_2): ", True)
            rubric["T1.10.02: first pass summaries match"] = True
        for (i,L) in newLs:
            o_fin7.insert(i,L)
        print("take output, add lineitems from premade list")
        o_fin7.manage_summaries()
        o_fin7.manageDropDownReplicas()
        o_fin7.updateSummaries()
        o_fin7_3 = o_fin7
        print("repeat manage summaries, manage ddr, update summaries")
        print("compare to standard")
        print("o_fin7_3: \n", o_fin7_3)
        print("s_fin7_3: \n", s_fin7_3)
        if not str(o_fin7_3) == str(s_fin7_3):
            print("str(o_fin7_3) == str(s_fin7_3): ",False)
            rubric["T1.10.03: increment summaries"] = False
            rubric["T1.10: confirmed"] = False
        else:
            print("str(o_fin7_3) == str(s_fin7_3): ",True)
            rubric["T1.10.03: increment summaries"] = True
        print("T1.10 finished. \n\n")
        #
        #
        #Task 1.11: summarize
        print("T1.11: check summarize() functionality")
        rubric["T1.11: confirmed"] = True
        o_fin8 = output["T1.11"]["fin8"]
        o_fin8a = copy.deepcopy(o_fin8)
        s_fin8_1 = standard["T1.11"]["fin8_1"]
        s_fin8_2 = standard["T1.11"]["fin8_2"]
        print("compare output and standard starting points")
        print("o_fin8: \n", o_fin8)
        print("s_fin8_1: \n", s_fin8_1)
        if not str(o_fin8) == str(s_fin8_1):
            print("str(o_fin8) == str(s_fin8_1): ", False)
            rubric["T1.11.01: starting points match"] = False
            rubric["T1.11: confirmed"] = False
        else:
            print("str(o_fin8) == str(s_fin8_1): ", True)
            rubric["T1.11.01: starting points match"] = True
        o_fin8.summarize()
        print("o_fin8.summarize()")
        print("o_fin8: \n", o_fin8)
        print("s_fin8_2: \n", s_fin8_2)
        if not str(o_fin8) == str(s_fin8_2):
            print("str(o_fin8) == str(s_fin8_2): ", False)
            rubric["T1.11.02: summarize views match"] = False
            rubric["T1.11: confirmed"] = False
        else:
            print("str(o_fin8) == str(s_fin8_2): ", True)
            rubric["T1.11.02: summarize views match"] = True
        o_fin8a.manage_summaries()
        o_fin8a.manageDropDownReplicas()
        o_fin8a.updateSummaries()
        print("run manage_summaries, manage ddr, update summaries on fin8a")
        print("result should be same as summarize()")
        if not o_fin8a == o_fin8:
            print("o_fin8a == o_fin8: ", False)
            rubric["T1.11.03: step equivalence to summarize"] = False
            rubric["T1.11: confirmed"] = False
        else:
            print("o_fin8a == o_fin8: ", True)
            rubric["T1.11.03: step equivalence to summarize"] = True
        print("T1.11 finished. \n\n")
        #
        #
        #Task 1.12: eraseManagedLineItems
        print("T1.12: check managed lineitem detection and clearing")
        rubric["T1.12: confirmed"] = True
        o_fin9 = output["T1.12"]["fin9"]
        s_fin9_1 = standard["T1.12"]["fin9_1"]
        s_fin9_2 = standard["T1.12"]["fin9_2"]
        print("compare output and standard starting points")
        print("o_fin9: \n", o_fin9)
        print("s_fin9_1: \n", s_fin9_1)
        if not str(o_fin9) == str(s_fin9_1):
            print("str(o_fin9) == str(s_fin9_1): ", False)
            rubric["T1.12.01: starting points match"] = False
            rubric["T1.12: confirmed"] = False
        else:
            print("str(o_fin9) == str(s_fin9_1): ", True)
            rubric["T1.12.01: starting points match"] = True
        o_fin9.eraseManagedLineItems()
        print("o_fin9.eraseManagedLineItems()")
        print("compare output and standard ending points")
        if not str(o_fin9) == str(s_fin9_2):
            print("str(o_fin9) == str(s_fin9_2): ", False)
            rubric["T1.12.02: cleared views match"] = False
            rubric["T1.12: confirmed"] = False
        else:
            print("str(o_fin9) == str(s_fin9_2): ", True)
            rubric["T1.12.02: cleared views match"] = True
        print("T1.12 finished. \n\n")
        #
        #
        #Task 1.13: reset
        print("T1.13: check full reset mechanism")
        rubric["T1.13: confirmed"] = True
        o_fin10 = output["T1.13"]["fin10"]
        s_fin10_1 = standard["T1.13"]["fin10_1"]
        s_fin10_2 = standard["T1.13"]["fin10_2"]
        print("compare output and standard starting points")
        print("o_fin10: \n", o_fin10)
        print("s_fin10_1: \n", s_fin10_1)
        if not str(o_fin10) == str(s_fin10_1):
            print("str(o_fin10) == str(s_fin10_1): ", False)
            rubric["T1.13.01: starting points match"] = False
            rubric["T1.13: confirmed"] = False
        else:
            print("str(o_fin10) == str(s_fin10_1): ", True)
            rubric["T1.13.01: starting points match"] = True
        o_fin10.reset()
        print("o_fin10.eraseManagedLineItems()")
        print("compare output and standard ending points")
        if not str(o_fin10) == str(s_fin10_2):
            print("str(o_fin10) == str(s_fin10_2): ", False)
            rubric["T1.13.02: reset views match"] = False
            rubric["T1.13: confirmed"] = False
        else:
            print("str(o_fin10) == str(s_fin10_2): ", True)
            rubric["T1.13.02: reset views match"] = True
        print("T1.13 finished. \n\n")
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
            print("Financials_01 passed: ", True)
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
