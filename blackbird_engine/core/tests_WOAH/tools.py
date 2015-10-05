#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.testing_tools
"""

Module provides shared convenience functions for tests. Test-specific functions
may include duplicates of functions found elsewhere in Blackbird to minimize
dependencies between the testing suite and the rest of the program. 
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
walk_dict()           convenience function for recursive dict comparisons

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a




#globals
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

#classes
#n/a
