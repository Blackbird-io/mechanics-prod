#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: tools.for_managers

"""

Module provides convenience functions for common content management tasks
handled by xManager modules (e.g., TopicManager, QuestionManager, etc.).
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
walk_package()        walk dir tree and apply action to modules that pass check

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import inspect




#globals
#n/a

#functions
def walk_package(top, check, action, counter = 0):
    """


    walk_package(top, check, action[, counter = 0]) -> int


    Function expects:
    ``top`` is a package module
    ``check`` is an attribute 
    ``action`` is a function with one argument
    ``counter`` tracks actions performed on package already
    
    Function walks through all modules within a package. When it encounters a
    module with a True ``check`` attribute, the function calls action() on
    that module. In other cases, function calls itself recursively.

    Function returns a counter showing the number of times it performed
    action on the package. 
    """
    for attr_name in dir(top):
        attr_val = getattr(top,attr_name)
        if not inspect.ismodule(attr_val):
            continue
        else:
            if getattr(attr_val,check,False):
                action(attr_val)
                counter += 1
            else:
                counter = walk_package(attr_val,
                                       check,
                                       action,
                                       counter)
                #pass own counter for incrementation, pick up count where
                #recursion call leaves off
    return counter


    
