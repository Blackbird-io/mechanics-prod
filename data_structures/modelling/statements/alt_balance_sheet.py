# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.statements.balance_sheet
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
from ..statement import Statement
from ..statement_bundle import StatementBundle




# Constants
# n/a

# Globals
# n/a

# Classes
class BalanceSheet(StatementBundle):
    #<-------------------------------------------------------------------------has to descend from Tags
    """
    A StatementBundle with individual statements for Assets, Liabilities, and
    Equity. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    as_of

    **statements**
    assets
    liabilities
    equity

    FUNCTIONS:
    check()
    ====================  ======================================================
    """
    ORDER = ("assets",
             "liabilities",
             "equity")
    
    def __init__(self, as_of):

        self.as_of = as_of
        
        self.assets = Statement("Assets")
        self.liabilities = Statement("Liabilities")
        self.equity = Statement("Equity")
        
    def check(self):
        """


        BalanceSheet.check() -> bool


        Return True iff instance Assets = Liabilities + Equity.
        """
        result = False

        A = None
        L = None
        E = None

        assignments = [(A, self.assets),
                       (L, self.liabilities),
                       (E, self.equities)
                       ]


        for counter, lines in assignments:
            for line in lines:
                if line.value:
                    counter += line.value

        if A == L + E:
            result = True

        return result

    
