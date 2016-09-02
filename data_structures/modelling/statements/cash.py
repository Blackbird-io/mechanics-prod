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
from ..line_item import LineItem



# Constants
# n/a

# Globals
# n/a

# Classes
class CashFlowStatement(Statement):
    def __init__(self, parent=None):
        Statement.__init__(self, name="cash flow statement", parent=parent)

        net_cash_line = LineItem('total net cash flow')
        self.add_top_line(net_cash_line)

        operating = LineItem(name="cash from operations")
        investing = LineItem(name="cash from investing")
        financing = LineItem(name="cash from financing")

        for line in [operating, investing, financing]:
            line.xl.format.blank_row_after = True
            net_cash_line.append(line)
