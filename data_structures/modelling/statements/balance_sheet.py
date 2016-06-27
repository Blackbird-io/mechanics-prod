# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.statements.sum_over_time_sheet
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
    add_line()            add line to instance at specified position
    add_line_to()         OBSOLETE; appends line to first line with given name
    add_top_line()        OBSOLETE; adds line to instance at top position
    append()              add line to instance in final position
    extend()              append multiple lines to instance in order
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

    def add_line(self, new_line, position=None):
        """


        BalanceSheet.add_line() -> None

        --``line`` is a LineItem
        --``position`` is the position at which to insert the LineItem

        Method delegates to Statement.add_line() to add line to instance.
        Method automatically sets all new lines to new_line.sum_over_time = False.
        """
        new_line.sum_over_time = False

        Statement.add_line(self, new_line, position=position)

    def add_line_to(self, line, *ancestor_tree):
        """


        BalanceSheet.add_line_to() -> None

        --``line`` is a LineItem
        --``ancestor_tree`` is  an iterable of LineItem string names

        Method delegates to Statement.add_line_to() to add line to instance.
        Method automatically sets all new lines to new_line.sum_over_time = False.
        """
        line.sum_over_time = False

        Statement.add_line_to(self, line, ancestor_tree)

    def add_top_line(self, line, after=None):
        """


        BalanceSheet.add_top_line() -> None

        --``line`` is a LineItem
        --``after`` is the name of the LineItem after which to insert the line

        Method delegates to Statement.add_top_line() to add line to instance.
        Method automatically sets all new lines to new_line.sum_over_time = False.
        """
        line.sum_over_time = False

        Statement.add_top_line(self, line, after=after)

    def append(self, line):
        """


        BalanceSheet.append() -> None

        --``line`` is a LineItem

        Method delegates to Statement.append() to add line to instance.
        Method automatically sets all new lines to new_line.sum_over_time = False.
        """
        line.sum_over_time = False

        Statement.append(self, line)

    def extend(self, lines):
        """


        BalanceSheet.extend() -> None

        --``lines`` is an interable containing LineItems

        Method delegates to Statement.extend() to add lines to instance.
        Method automatically sets all new lines to new_line.sum_over_time = False.
        """
        for line in lines:
            line.sum_over_time = False

        Statement.extend(self, lines)