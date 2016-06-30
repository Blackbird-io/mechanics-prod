# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.financials
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

from .statement import Statement

from .statements import Overview, Income, CashFlow, BalanceSheet
from .statement_bundle import StatementBundle
from .equalities import Equalities

from data_structures.system.bbid import ID




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
    balance               BalanceSheet; starting and ending balance for object
    cash                  Statement; cash flow statement for object
    has_valuation         bool; whether the object has a non-blank valuation
    income                Statement; income statement for object
    ledger                placeholder for object general ledger
    overview              Statement; general data about an object
    valuation             Statement; business valuation for the object

    FUNCTIONS:
    copy                  return deep copy
    ====================  ======================================================
    """
    ORDER = ("overview", "income", "cash", "ending", "ledger")
    FULL_ORDER = ("overview", "income", "cash", "starting", "ending", "ledger",
                  "valuation")
    # tuple for immutability
    
    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = CashFlow()
        self.valuation = Statement("Valuation")
        self.starting = BalanceSheet("Starting Balance Sheet")
        self.ending = BalanceSheet("Ending Balance Sheet")
        self.ledger = None
        self.id = ID()  # does not get its own bbid, just holds namespace

    @property
    def has_valuation(self):
        return not self.valuation == Statement("Valuation")

    def __str__(self):
        
        result = "\n"

        if Equalities.multi_getattr(self, "relationships.parent", None):

            header = "Financial statements for " + str(self.relationships.parent.tags.name)
            header = header.center(bb_settings.SCREEN_WIDTH)
            header += "\n\n"

            starting = "Period starting: " + str(self.relationships.parent.period.starting)
            starting = starting.center(bb_settings.SCREEN_WIDTH)
            starting += "\n"

            header += starting

            ending = "Period ending:   " + str(self.relationships.parent.period.ending)
            ending = ending.center(bb_settings.SCREEN_WIDTH)
            ending += "\n"

            header += ending
            header += "\n"

            result += header

        border = "***"
        border = border.center(bb_settings.SCREEN_WIDTH) + "\n\n"

        result += border

        self.ORDER = ("overview", "income", "cash", "starting", "ending",
                      "ledger")

        # Use a special tuple that includes all statements to block the default
        # class order.
        result += StatementBundle.__str__(self)
        del self.ORDER

        result += "\n"
        result += border

        return result        

    def copy(self):
        """


        Financials.copy() -> Financials


        Return a deep copy of instance.

        Method starts with a shallow copy and then substitutes deep copies
        for the values of each attribute in instance.ORDER
        """
        new_instance = copy.copy(self)

        self.ORDER = ("overview", "income", "cash", "starting", "ending",
                      "ledger", "valuation")

        for name in self.ORDER:
            own_statement = getattr(self, name, None)
            if own_statement is not None:
                new_statement = own_statement.copy()
                setattr(new_instance, name, new_statement)

        del self.ORDER

        return new_instance

    def register(self, namespace):
        """


        Financials.register() -> None

        --``namespace`` is the namespace to assign to instance

        Method sets namespace of instance, does not assign an actual ID.
        Registers statements on instance.
        """
        self.id.set_namespace(self.id.namespace)

        for statement in self.full_ordered:
            if statement:
                statement.register(self.id.namespace)
