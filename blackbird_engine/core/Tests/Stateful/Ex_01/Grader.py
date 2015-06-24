#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BUCopy_02.Grader

#Syllabus:
#Use function to check for equality and identity
#Compare (o,c1), (c2,cc3), (o,s), (o_c2,s_c2)
#------------------------------------------------------------------------------------------------currently does not use a standard file
#use blank file for speed.

from ..BUCopy_01 import Grader as Gr1

import copy
import dill
import sys
import traceback

bu_compare = Gr1.bu_compare

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
        o_topBU = o["T14.01"]["topBU"]
        comp_bbid = o["T14.02"]["lab_comp_bbid"]
        dr_bbid = o["T14.02"]["lab_dr_bbid"]
        t_dnt = o["T14.02"]["t_dnt"]
        c1 = o["T14.03"]["c1"]
        c2 = o["T14.03"]["c2"]
        cc3 = o["T14.03"]["cc3"]
        var_header = ""
        var_header += "\n\n"
        var_header += "\t"+"""o = result["output"]\n"""
        var_header += "\t"+"""o_topBU = o["T14.01"]["topBU"]\n"""
        var_header += "\t"+"""comp_bbid = o["T14.02"]["lab_comp_bbid"]\n"""
        var_header += "\t"+"""dr_bbid = o["T14.02"]["lab_dr_bbid"]\n"""
        var_header += "\t"+"""t_dnt = o["T14.02"]["t_dnt"]\n"""
        var_header += "\t"+"""c1 = o["T14.03"]["c1"]\n"""
        var_header += "\t"+"""c2 = o["T14.03"]["c2"]\n"""
        var_header += "\t"+"""cc3 = o["T14.03"]["cc3"]\n\n"""
        var_header = var_header.expandtabs(4)
        print(var_header)
        #
        #14.01
        t_root = "T14.01"
        t_header = "\t"+t_root+": o_topBU vs c1"
        t_header = t_header.expandtabs(4)
        print(t_header)
        bu_compare(o_topBU,
                   c1,
                   t_root,
                   tab_width = 4,
                   o_caption = "(o_topBU)",
                   c_caption = "(c1)",
                   show_desc = True,
                   trace = True,
                   r = rubric)                  
        t_footer = "\t" + t_root + " finished. \n\n"
        t_footer = t_footer.expandtabs(4)
        print(t_footer)
        #
        #14.02
        t_root = "T14.02"
        conf_key = t_root + ": confirmed"
        rubric[conf_key] = True
        #
        t_header = "\t"+t_root+": ``do-not-touch`` tag should not travel out"
        t_header = t_header.expandtabs(4)
        print(t_header)
        #
        dr_orig = o_topBU.components[comp_bbid].drivers.dr_directory[dr_bbid]
        dr_copy = c1.components[comp_bbid].drivers.dr_directory[dr_bbid]
        p = ""
        p += """\tdr_orig = o_topBU.components[comp_bbid].drivers.dr_directory[dr_bbid]\n"""
        p += """\tdr_copy = c1.components[comp_bbid].drivers.dr_directory[dr_bbid]\n"""
        p.expandtabs(4)
        print(p)
        p = ""
        p += "\t**t_dnt**: %s\n\n" % t_dnt
        p += "\tdr_orig.allTags: \n\t%s\n\n" % dr_orig.allTags
        p += "\tdr_copy.allTags: \n\t%s\n\n" % dr_copy.allTags
        p.expandtabs(4)
        print(p)
        #
        s = "\tt_dnt in dr_copy.allTags: %s"
        p_header="\tRule prohibiting ``do not touch`` tags going out in force: %s\n"
        p_sub_key = t_root + ".01: tag rules enforced correctly."
        if t_dnt in dr_copy.allTags:
            s = s % str(True)
            s.expandtabs(4)
            print(s)
            p_header = p_header % str(False)
            p_header.expandtabs(4)
            print(p_header)
            rubric[p_sub_key] = False
            rubric[conf_key] = False
        else:
            s = s % str(False)
            s.expandtabs(4)
            print(s)
            p_header = p_header % str(True)
            p_header.expandtabs(4)
            print(p_header)
            rubric[p_sub_key] = True
        t_footer = "\t"+t_root + " finished. \n\n"
        t_footer = t_footer.expandtabs(4)
        print(t_footer)
        #
        #14.03
        t_root = "T14.03"
        #keep t_root plain so can use for rubric
        t_header = "\t"+t_root+": c2 vs cc3 (copy of a copy, periods blank)."
        t_header = t_header.expandtabs(4)
        print(t_header)
        bu_compare(c2,
                   cc3,
                   t_root,
                   tab_width = 4,
                   o_caption = "(c2, period blank)",
                   c_caption = "(cc3, period blank)",
                   show_desc = False,
                   trace = True,
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
                print("BUCopy_02 passed: ", False)
                print("*"*80)
                print("*"*80)
                break
            else:
                continue
        else:
            print("*"*80)
            print("*"*80)
            print("BUCopy_02 passed: ", True)
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
    
