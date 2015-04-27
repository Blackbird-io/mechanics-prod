#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BUCopy_01.Grader

#Syllabus:
#Use function to check for equality and identity
#Compare (o,c1), (c2,cc3), (o,s), (o_c2,s_c2)
#------------------------------------------------------------------------------------------------currently does not use a standard file
#use blank file for speed.

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

def bu_compare(orig_bu,
               copy_bu,
               root_key,
               tab_width = 4,
               o_caption = None,
               c_caption = None,
               show_desc = True,
               trace = True,
               r = None
               ):
    """

    compare(xbu,ybu) -> bool

    checks that:
       compares equal
       components point to distinct objects
       drivers point to distinct object
       financials point to distinct objects
       period points to the same object
    if any are false, false
    
    test_key is the "T12.01" root.
    iff show_desc is True, print description of each Part (use for first call)

    function expects a dictionary-type object called ``rubric`` to exist in
    the namespace where it is called. function records its results there.

    function records the initial conf_key = True.

    function also prints separators. 
    """
    rubric = r
    #
    #Make a "Test x.x: confirmed" key for result tracking
    #(keys should always be untabbed)
    conf_key = root_key+": confirmed"
    rubric[conf_key] = True
    #
    #define utility function for convenience
    def tabbed_print(s, tw = tab_width):
        s = s.expandtabs(tw)
        #pick up tab_width from enclosing bu_compare scope
        #print w user specified tabs
        print(s)
    #
    dashes = "\t"+(80-tab_width*2)*"-"+"\n"
    tabbed_print(dashes)
    #
    lead = ""
    lead += "\tThis function checks that the original and copy objects maintain\n"
    lead += "\tthe correct relationship.\n"
    lead += "\n"
    lead += "\tSpecifically, the function checks that:\n"
    lead += "\t  1. equality is True for the original and copy as a whole.\n"
    lead += "\t  2. original and copy ``components`` point to distinct sets\n"
    lead += "\t     of objects (identity is False for each pair of matching-\n"
    lead += "\t     bbid business units).\n"
    lead += "\t  3. original and copy ``drivers`` point to distinct sets of\n"
    lead += "\t     objects in their .dr_directory.\n"
    lead += "\t  4. original and copy ``financials`` point to lists of\n"
    lead += "\t     distinct objects (matching-index lineitems must have\n"
    lead += "\t     identity False).\n"
    lead += "\t  5. original and copy ``period`` points to the same object.\n"
    lead += "\n"
    lead += "\tFunction returns False if the arguments fail any part above, and\n"
    lead += "\tTrue otherwise.\n"
    lead += "\n"
    lead += "\tObjects (like Business Units) that define a class-specific \n"
    lead += "\tequality method usually require equality among key attributes.\n"
    lead += "\tFor Business Units, that means that Part 1 of this function's\n"
    lead += "\talready requires that each matching component, driver, and line\n"
    lead += "\tcompare equal."
    lead += "\n\n"
    if show_desc:
        tabbed_print(lead)
    l1 = "\t**original object**: \n\t%s\n"
    if o_caption:
        l1 = l1 + "\t" + o_caption + "\n"
    l2 = "\t**copy object**:     \n\t%s\n"
    if c_caption:
        l2 = l2 + "\t"+ c_caption + "\n"
    l1 = l1 % orig_bu
    l2 = l2 % copy_bu
    tabbed_print(l1)
    tabbed_print(l2)
    #
    #
    #Part 1
    p_lead = "\tPart 1: Check for equality between original and copy.\n"
    tabbed_print(p_lead)
    #
    p1_header = "\t"+"orig_bu == copy_bu: "
    p1_sub_key = root_key + ".01: original equals copy"
    if not orig_bu == copy_bu:
        p1_header = p1_header + str(False)
        tabbed_print(p1_header)
        rubric[p1_sub_key]=False
        rubric[conf_key] = False
        if trace:
            #
            #.__eq__(trace = True) will print detailed equality analysis
            #
            detail_tw = tab_width+4
            orig_bu.__eq__(copy_bu,trace = True, tab_width = detail_tw)
            #
            #
    else:
        p1_header = p1_header + str(True)
        tabbed_print(p1_header)
        rubric[p1_sub_key]=True
    print("\n\n")
    #
    #
    #Part 2
    p_lead = "\tPart 2: Check that components are distinct.\n"
    tabbed_print(p_lead)
    #
    p2_desc = ""
    p2_desc += "\tIterate through each of the bbids in the original's\n"
    p2_desc += "\tcomponents. For each bbid, pull the component from the\n"
    p2_desc += "\toriginal and from the copy. If identity is true for the two\n"
    p2_desc += "\tcomponents, break loop and fail part. Otherwise, continue.\n"
    p2_desc += "\n"
    p2_desc += "\tIf each component is distinct, the args pass Part 2.\n"
    #
    if show_desc:
        tabbed_print(p2_desc)
    #
    p2_header = ""
    p2_header += "\tIdentity violation detected for bbid: \n%s\n"
    p2_header += "\to.components[bbid] is c.components[bbid]\n"
    #
    p2_alt = ""
    p2_alt += "\t All component business units are distinct.\n"
    #
    p2_sub_key = root_key + ".02: components are distinct."
    #
    tw2 = tab_width*2
    #
    for bbid in orig_bu.components.keys():
        if orig_bu.components[bbid] is copy_bu.components[bbid]:
            p2_header = p2_header % bbid
            tabbed_print(p2_header,tw = tw2)
            rubric[p2_sub_key] = False
            rubric[conf_key] = False
            break
        else:
            continue
    else:
        tabbed_print(p2_alt,tw = tw2)
        rubric[p2_sub_key] = True
    print("\n\n")
    #
    #
    #Part 3
    p_lead = "\tPart 3: Check that drivers are distinct.\n"
    tabbed_print(p_lead)
    #
    p_desc = ""
    p_desc += "\tIterate through each of the bbids in the original's\n"
    p_desc += "\tdrivers.dr_directory.keys(). For each bbid, pull the driver\n"
    p_desc += "\tfrom the original and copy. If the two drivers share identity,\n"
    p_desc += "\tbreak loop and fail part. Otherwise, continue.\n"
    p_desc += "\n"
    p_desc += "\tIf each driver is distinct, the args pass Part 3.\n"
    #
    if show_desc:
        tabbed_print(p_desc)
    #
    p_header = ""
    p_header += "\tIdentity violation detected for bbid: \n%s\n"
    p_header += "\to.drivers.dr_directory[bbid] is c.drivers.dr_directory[bbid]\n"
    #
    p_alt = ""
    p_alt += "\t All drivers are distinct.\n"
    #
    p_sub_key = root_key + ".03: drivers are distinct."
    #
    tw2 = tab_width*2
    #
    orig_drs = orig_bu.drivers.dr_directory
    copy_drs = copy_bu.drivers.dr_directory
    for bbid in orig_drs.keys():
        if orig_drs[bbid] is copy_drs[bbid]:
            p_header = p_header % bbid
            tabbed_print(p_header,tw = tw2)
            rubric[p_sub_key] = False
            rubric[conf_key] = False
            break
        else:
            continue
    else:
        tabbed_print(p_alt,tw = tw2)
        rubric[p_sub_key] = True
    print("\n\n")
    #
    #
    #Part 4
    p_lead = "\tPart 4: Check that each line in financials is distinct.\n"
    tabbed_print(p_lead)
    #
    p_desc = ""
    p_desc += "\tIterate through a zip of original and copy financials. Check\n"
    p_desc += "\tfor identity in each pair. Pairs already must have equality\n"
    p_desc += "\tper Part 1.\n"
    #
    if show_desc:
        tabbed_print(p_desc)
    #
    p_header = ""
    p_header += "\tIdentity violation detected for line: \n%s\n"
    p_header += "\tLine is the same object in original and copy.\n"
    #
    p_alt = ""
    p_alt += "\t All lines are distinct.\n"
    #
    p_sub_key = root_key + ".04: financials are distinct."
    #
    tw2 = tab_width*2
    #
    orig_fins = orig_bu.financials
    copy_fins = copy_bu.financials
    for (orig_l, copy_l) in zip(orig_fins, copy_fins):
        if orig_l is copy_l:
            p_header = p_header % orig_line
            tabbed_print(p_header,tw = tw2)
            rubric[p_sub_key] = False
            rubric[conf_key] = False
            break
        else:
            continue
    else:
        tabbed_print(p_alt,tw = tw2)
        rubric[p_sub_key] = True
    print("\n\n")
    #
    #
    #Part 5
    p_lead = "\tPart 5: Check that copy period is original period.\n"
    tabbed_print(p_lead)
    #
    p_header = "\t"+"orig_bu.period is copy_bu.period: "
    p_sub_key = root_key + ".05: period identity"
    if not orig_bu.period is copy_bu.period: 
        p_header = p_header + str(False)
        tabbed_print(p_header)
        rubric[p_sub_key] = False
        rubric[conf_key] = False
    else:
        p_header = p_header + str(True)
        tabbed_print(p_header)
        rubric[p_sub_key] = True
    print("\n\n")
    #
    #
    footer = ""
    footer += "\tTest completed.\n"
    footer += dashes + dashes
    tabbed_print(footer)
    #    

def check(result,standard):
    global rubric
    rubric = {}
    global passed
    passed = True
    try:
        o = result["output"]
        o_topBU = o["T13.01"]["topBU"]
        c1 = o["T13.01"]["c1"]
        c2 = o["T13.01"]["c2"]
        cc3 = o["T13.01"]["cc3"]
        var_header = ""
        var_header += "\n\n"
        var_header += "\t"+"""o = result["output"]\n"""
        var_header += "\t"+"""o_topBU = o["T13.01"]["topBU"]\n"""
        var_header += "\t"+"""c1 = o["T13.01"]["c1"]\n"""
        var_header += "\t"+"""c2 = o["T13.01"]["c2"]\n"""
        var_header += "\t"+"""cc3 = o["T13.01"]["cc3"]\n\n"""
        var_header = var_header.expandtabs(4)
        print(var_header)
        #
        #13.01
        t_root = "T13.01"
        t_header = "\t"+t_root+": o_topBU vs c1"
        t_header = t_header.expandtabs(4)
        print(t_header)
        bu_compare(o_topBU,
                   c1,
                   t_root,
                   o_caption = "(o_topBU)",
                   c_caption = "(c1)",
                   show_desc = True,
                   r = rubric)                  
        t_footer = "\t" + t_root + " finished. \n\n"
        t_footer = t_footer.expandtabs(4)
        print(t_footer)
        #
        #
        #13.02
        t_root = "T13.02"
        #keep t_root plain so can use for rubric
        t_header = "\t"+t_root+": c2 vs cc3 (copy of a copy, periods blank)."
        t_header = t_header.expandtabs(4)
        print(t_header)
        bu_compare(c2,
                   cc3,
                   t_root,
                   o_caption = "(c2, period blank)",
                   c_caption = "(cc3, period blank)",
                   show_desc = False,
                   r = rubric)                  
        #
        t_footer = "\t" + t_root + " finished. \n\n"
        t_footer = t_footer.expandtabs(4)
        print(t_footer)
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
                print("BUCopy_01 passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("BUCopy_01 passed: ", True)
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
    
