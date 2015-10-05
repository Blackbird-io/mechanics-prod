#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: alt_TagManager.TagRule
"""

Module defines TagRule class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TagRule               dictionary of ModeRules keyed by event code
====================  ==========================================================
"""





from .ModeRule import ModeRule





class TagRule(dict):
    """

    The TagRules class provides dictionaries with a standard set of keys, each
    pointing to its own ModeRule instance.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    modes                 list; CLASS standard fields
    

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    modes = ["at","out","up"]
    def __init__(self):
        dict.__init__(self)
        for m in self.modes:
            self[m] = ModeRule()


    
        
