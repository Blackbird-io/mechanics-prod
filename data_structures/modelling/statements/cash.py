# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.statements.cash
"""

Module defines a custom statement for cash flows
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
CashFlowStatement     statement that may contain specialized info
====================  ==========================================================
"""




# Imports
from ..statement import Statement




# Constants
# n/a

# Globals
# n/a

# Classes
class CashFlowStatement(Statement):
    def __init__(self, parent=None):
        Statement.__init__(self, name="cash flow statement", parent=parent)
