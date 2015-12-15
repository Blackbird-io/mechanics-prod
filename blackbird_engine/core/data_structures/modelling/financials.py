#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.financials
"""

Module defines Financials, a bundle of common statements. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Financials            a StatementBundle with income, cash, balance and others.
====================  ==========================================================
"""




# Imports
from .statements import Overview, Income, CashFlow, BalanceSheet
from .statement_bundle import StatementBundle




# Constants
# n/a

# Globals
# n/a

# Classes
class Financials(StatementBundle):
    """

    A StatementBundle that includes standard financial statements. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    overview              Statement; general data about an object
    income                Statement; income statement for object
    cash                  Statement; cash flow statement for object
    balance               BalanceSheet; starting and ending balance for object
    ledger                placeholder for object general ledger

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    ORDER = ("overview",
             "income",
             "cash",
             "starting",
             "ending",
             "ledger")
    # tuple for immutability
    
    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = CashFlow()
        self.starting = BalanceSheet("Starting Balance Sheet")
        self.ending = BalanceSheet("Ending Balance Sheet")
        self.ledger = None

    def link(self, source):
        self.source = source
        self.starting = source.ending
        
        

    
