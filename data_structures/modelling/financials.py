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
import copy

from .statements import Overview, Income, CashFlow, BalanceSheet
from .statement_bundle import StatementBundle
from .equalities import Equalities




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
    copy                  return deep copy
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

        if Equalities.multi_getattr(self, "tags.parentObject", None):

            header = "Financial statements for " + str(self.tags.parentObject.tags.name)
            header = header.center(bb_settings.SCREEN_WIDTH)
            header += "\n\n"

            starting = "Period starting: " + str(self.tags.parentObject.period.starting)
            starting = starting.center(bb_settings.SCREEN_WIDTH)
            starting += "\n"

            header += starting

            ending =  "Period ending:   " + str(self.tags.parentObject.period.ending)
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

    def copy(self, enforce_rules=True):
        """


        Financials.copy() -> Financials


        Return a deep copy of instance.

        Method starts with a shallow copy and then substitutes deep copies
        for the values of each attribute in instance.ORDER
        """
        new_instance = copy.copy(self)

        self.ORDER = ("overview", "income", "cash", "starting", "ending", "ledger")

        for name in self.ORDER:
            own_statement = getattr(self, name, None)
            if own_statement is not None:
                new_statement = own_statement.copy(enforce_rules)
                setattr(new_instance, name, new_statement)

        del self.ORDER

        return new_instance
    
