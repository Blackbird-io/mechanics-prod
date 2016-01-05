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
import bb_settings

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
    ORDER = ("overview", "income", "cash", "ending", "ledger")
    # tuple for immutability
    
    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = CashFlow()
        self.starting = BalanceSheet("Starting Balance Sheet")
        self.ending = BalanceSheet("Ending Balance Sheet")
        self.ledger = None

    def __str__(self):
        
        result = "\n"

        if getattr(self, "parentObject", None):

            header = "Financial statements for " + str(self.parentObject.name)
            header = header.center(bb_settings.SCREEN_WIDTH)
            header += "\n\n"

            starting = "Period starting: " + str(self.parentObject.period.starting)
            starting = starting.center(bb_settings.SCREEN_WIDTH)
            starting += "\n"

            header += starting

            ending =  "Period ending:   " + str(self.parentObject.period.ending)
            ending = ending.center(bb_settings.SCREEN_WIDTH)
            ending += "\n"

            header += ending
            header += "\n"

            result += header

        border = "***"
        border = border.center(bb_settings.SCREEN_WIDTH) + "\n\n"

        result += border
        
        self.ORDER = ("overview", "income", "cash", "starting", "ending", "ledger")
        # Use a special tuple that includes all statements to block the default
        # class order.
        result += StatementBundle.__str__(self)
        del self.ORDER
        # unblock

        result += "\n"
        result += border

        return result        
        

    
