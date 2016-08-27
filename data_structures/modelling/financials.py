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
        self._full_order = ["overview", "income", "cash", "starting", "ending",
                           "ledger", "valuation"]
        self._compute_order = ['overview', 'income', 'cash']


    @property
    def compute_order(self):
        return self._compute_order.copy()

    @property
    def full_order(self):
        return self._full_order.copy()

    @property
    def full_ordered(self):
        """

        **read-only property**

        Return list of attribute values for all names in instance.full_order.
        """
        result = []

        for name in self.full_order:
            statement = getattr(self, name)
            result.append(statement)

        return result

    @property
    def has_valuation(self):
        return not self.valuation == Statement("Valuation")

    @property
    def order(self):
        order = self.full_order
        order.remove('starting')
        order.remove('valuation')

        return order

    @property
    def ordered(self):
        """

        **read-only property**

        Return list of attribute values for all names in instance.order
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

    def add_statement(self, name, statement=None, title=None, position=None,
                      compute=True):
        """

        Financials.add_statement() -> None

        --``name`` is the string name for the statement attribute
        --``statement`` is optionally the statement to insert, if not provided
                        a blank statement will be added
        --``title`` is optionally the name to assign to the statement object,
                    if not provided ``name`` will be used
        --``position`` is optionally the index at which to insert the statement
                       in instance.full_order
        --``compute`` bool; default is True, whether or not to include the
                      statement in computation order  during fill_out (will be
                      computed between starting and ending balance sheets) or
                      whether to compute manually after

        Method adds a new statement to the instance and inserts it at specified
        position in instance.full_order.  If no position is provided, the
        new statement will be added at the end.
        """

        if not statement:
            use_name = title or name
            statement = Statement(use_name)

        setattr(self, name, statement)

        if position:
            self._full_order.insert(position, name)
        else:
            self._full_order.append(name)

        if compute:
            # include statement to be computed during fill_out in the same
            # order it is in full_order
            full = set(self.full_order)
            comp = set(self._compute_order) | {name}

            rem_terms = full - comp

            new_compute = self.full_order
            for term in rem_terms:
                new_compute.remove(term)

            self._compute_order = new_compute

    def build_tables(self):
        """


        Financials.build_tables() -> None


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
