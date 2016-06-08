# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: flow.level

"""

Module defines the Level class. Level objects store items and provide some
descriptive attributes.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Level                 list that groups items by priority
====================  ==========================================================
"""




#imports
from data_structures.guidance.guide import Guide




#globals
#n/a

#classes
class Level(list):
    """

    Level objects provide a specialized list with two descriptive attributes.
    Other modules use Level objects to group items of equal priority. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    guide                 instance of Guide object                 
    last                  int, index where user stopped analysis

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        list.__init__(self)
        self.guide = Guide()
        self.last = 0
