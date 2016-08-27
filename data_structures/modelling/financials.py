# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.financials
"""

Module defines Financials, a bundle of common statements with the ability to
add custom statements as desired.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Financials            a dynamic class that holds standard and custom statements
====================  ==========================================================
"""




# Imports
import bb_settings
import copy

from .statement import Statement
from .statements import Overview, Income, CashFlow, BalanceSheet
from .equalities import Equalities

from data_structures.system.bbid import ID




# Constants
# n/a

# Globals
# n/a

# Classes
class Financials:
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

    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = CashFlow()
        self.valuation = Statement("Valuation")
        self.starting = BalanceSheet("Starting Balance Sheet")
        self.ending = BalanceSheet("Ending Balance Sheet")
        self.ledger = None
        self.id = ID()  # does not get its own bbid, just holds namespace
        self.full_order = ["overview", "income", "cash", "starting", "ending",
                           "ledger", "valuation"]

    @property
    def full_ordered(self):
        """


        **read-only property**


        Return list of attribute values for all names in instance.FULL_ORDER.
        """
        result = []

        try:
            order = self.full_order
        except AttributeError:
            order = self.FULL_ORDER

        for name in order:
            statement = getattr(self, name)
            result.append(statement)

        return result

    @property
    def has_valuation(self):
        return not self.valuation == Statement("Valuation")

    @property
    def order(self):
        try:
            order = self.full_order.copy()
        except AttributeError:
            order = list(self.FULL_ORDER.copy())

        order.remove('starting')
        order.remove('valuation')
        return order

    @property
    def FULL_ORDER(self):
        """
        OBSOLETE
        """
        return ("overview", "income", "cash", "starting", "ending",
                           "ledger", "valuation")

    @property
    def ordered(self):
        """


        **read-only property**


        Return list of attribute values for all names in instance.ORDER.
        """
        result = []
        for name in self.order:
            statement = getattr(self, name)
            result.append(statement)

        return result

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

        result = ""
        for statement in self.full_ordered:
            if statement is not None:
                result += str(statement)

        result += "\n"
        result += border

        return result        

    def build_tables(self):
        """


        StatementBundle.build_tables() -> None


        Build tables for each defined statement.
        """
        self.run_on_all("build_tables")

    def copy(self):
        """


        Financials.copy() -> Financials


        Return a deep copy of instance.

        Method starts with a shallow copy and then substitutes deep copies
        for the values of each attribute in instance.ORDER
        """
        new_instance = copy.copy(self)

        for name in self.full_order:
            own_statement = getattr(self, name, None)
            if own_statement is not None:
                new_statement = own_statement.copy()
                setattr(new_instance, name, new_statement)

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

    def reset(self):
        """


        StatementBundle.reset() -> None


        Reset each defined statement.
        """
        self.run_on_all("reset")

    def run_on_all(self, action, *kargs, **pargs):
        """


        Bundle.run_on_all() -> None


        Run ``statement.action(*kargs, **pargs)`` for all defined statements
        in instance.ordered.

        Expects ``action`` to be a string naming the statement method.
        """
        for statement in self.ordered:
            if statement is not None:
                routine = getattr(statement, action)
                routine(*kargs, **pargs)

    def summarize(self):
        """


        StatementBundle.summarize() -> None


        Summarize each defined statement.
        """
        self.run_on_all("summarize")
