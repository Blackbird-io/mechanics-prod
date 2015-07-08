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
walk_dict()           convenience function for recursive dict comparisons

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
    """


    printRubric(r[, width = 60]) -> tuple


    Function prints the Grader rubric nicely and returns a tuple of results.
    """
    print("RUBRIC:\n")
    ks = list(r.keys())
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
        print(k, dots, r[k])
    return (stepks, confks)

def walk_dict(std, new, tab = 4):
    """


    walk_dict(std, new[, tab = 4]) -> bool


    Function returns True if for each k in ``std``, std[k] == new[k], or, if
    std[k] is a dictionary instance, that the function returns True when
    comparing the values.

    Function returns false otherwise.
    """
    c = """
    \tRunning walk_dict() for the following:
    
    \tstd = %s
    \tnew = %s
    \ttab = %s
    
    """
    c = c % (std, new, tab)
    print(c.expandtabs(tab))
    #
    outcome = True
    c = "\toutcome = True"
    print(c.expandtabs(tab))
    #
    known_keys = std.keys()
    c = "\tknown_keys = std.keys()\n"
    print(c.expandtabs(tab))
    #
    c = """
    \tStep through the keys in ``std``. If value is a dictionary, call the
    \tfunction recursively for std[k] and new[k]. Otherwise, check that value
    \tequals new value.

    Return True if all the values match, False otherwise.

    \tfor (i,k) in enumerate(known_keys):    
        \tknown_value = std[k]
        \tnew_value = new[k]
        \t...

    \tNow running loop:
    """
    for (i,k) in enumerate(known_keys):
        known_value = std[k]
        new_value = new[k]
        #
        c = ""
        c += "\t%s. Key: ``%s``\n\n" % (i,k)
        c += "\t    Known value: \n    \t%s\n\n" % known_value
        c += "\t    New value:   \n    \t%s\n\n" % new_value
        c = c.expandtabs(tab)
        print(c)
        #
        if isinstance(known_value, dict):
            try:
                sub_tab = tab + 4
                sub_outcome = walk_dict(known_value, new_value, tab = sub_tab)
                if not sub_outcome:
                    outcome = False
                    #
                    c = "\tSetting outcome to False due negative sub outcome:\n\n"
                    c += "\tsub_outcome = %s\n" % sub_outcome
                    c += "\toutcome = %s\n" % outcome
                    c = c.expandtabs(tab)
                    print(c)
                    #
            except Exception as X:
                #
                c = "\tEncountered exception: \n\t%s\n" % X
                c = c.expandtabs(tab)
                print(c)
                #
                c = "\tSetting outcome to False"
                c= c.expandtabs(tab)
                print(c)
                #
                outcome = False
                c = "\toutcome = %s" % outcome
                c= c.expandtabs(tab)
                print(c)
                #
                continue
        else:
            if known_value != new_value:
                c = "\tknown value != new value"
                c = c.expandtabs(tab)
                print(c)
                outcome = False
            else:
                continue
    else:
        print("\n")
    #
    c = "\toutcome = %s\n" % outcome
    c = c.expandtabs(tab)
    print(c)
    #
    c = "\treturn outcome\n\n\t--\n\n\n"
    c = c.expandtabs(tab)
    print(c)
    #
    return outcome

def check(result,standard):
    """


    check(result, standard) -> tuple


    Function checks whether result satisfies standard. Returns bool result
    and scoring rubric. 
    """
    #
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
        c = """

        Check that new credit references contain all of the standard data. New
        references can pass even when they contain additional data (that does
        not exist in old references).
        
        """
        print(c)
        #
        c = """

        outcome = walk_dict(std_references, new_references)
        
        """
        print(c)
        outcome = walk_dict(std_references, new_references)
        #
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
