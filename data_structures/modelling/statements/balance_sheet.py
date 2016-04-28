#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.statements.balance_sheet
"""

Module definesf BalanceSheet, a StatementBundle with Assets, Liabilities, and
Equity.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BalanceSheet          objects include assets, liabilities, and equity
====================  ==========================================================
"""




# Imports
from ..line_item import LineItem
from ..statement import Statement




# Constants
# n/a

# Globals
# n/a

# Classes
class BalanceSheet(Statement):
    """

    []
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    as_of

    FUNCTIONS:
    check()
    ====================  ======================================================
    """
    def __init__(self, name, as_of=None):
        
        Statement.__init__(self, name)

        self.as_of = as_of

        assets = LineItem(name="Assets")
        liabilities = LineItem(name="Liabilities")
        equity = LineItem(name="Equity")

        for line in [assets, liabilities, equity]:
            self.add_top_line(line)

      #can add custom str that shows as of date
        
##    def check(self):
##        """
##
##
##        BalanceSheet.check() -> bool
##
##
##        Return True iff instance Assets = Liabilities + Equity.
##        """
##        result = False
##
##        A = None
##        L = None
##        E = None
##
##        assignments = [(A, self.assets),
##                       (L, self.liabilities),
##                       (E, self.equities)
##                       ]
##
##
##        for counter, lines in assignments:
##            for line in lines:
##                if line.value:
##                    counter += line.value
##
##        if A == L + E:
##            result = True
##
##        return result
##
##    
