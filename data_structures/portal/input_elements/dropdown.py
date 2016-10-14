# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.dropdown
"""

Module defines the DropdownInput class. Portal displays DropdownInput objects
as drop-down menus.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DropdownInput         Describes a drop-down field
====================  ==========================================================
"""




# imports
from .choice import ChoiceInput




# globals
# n/a

# classes
class DropdownInput(ChoiceInput):
    """

    The DropdownInput defines an input element that forces user to select a
    response from a menu of options, explicitly a drop-down menu.

    The DropdownInput decends from ChoiceInput.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    # n/a

    FUNCTIONS:
    # n/a
    ====================  =====================================================
    """
    def __init__(self):
        ChoiceInput.__init__(self)
        self.__dict__["input_type"] = "drop-down"
