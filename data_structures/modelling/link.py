#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.modelling.link
"""

Module defines Link class, which is a LineItem class specifically for path.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Link                  a LineItem with a pointer to a target business unit
====================  =========================================================
"""




# Imports
from .line_item import LineItem




# Constants
# n/a

# Classes
class Link(LineItem):
    """

    A Link is a LineItem that can have a target attribute.

    Link is a class specifically designed to be added to PATH to redirect
    focus to a target business unit.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    target                pointer to BusinessUnit where focus should be shifted

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    def __init__(self, target):
        LineItem.__init__(self, target.name)
        self.target = target
