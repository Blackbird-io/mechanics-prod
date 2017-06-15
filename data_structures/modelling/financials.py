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
import logging

import bb_settings
import bb_exceptions

from data_structures.serializers.chef.data_management import LineData
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from .line_item import LineItem
from .link import Link
from .statement import Statement
from .statements import BalanceSheet
from .statements import CashFlow
from .equalities import Equalities




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)


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
    get_covenant_statements method returns list of instances covenants statements
    get_kpi_statements      method returns list of instances kpi statements
    get_regular_statements  method returns list of instances regular statements
    ====================  ======================================================
    """
    OVERVIEW_NAME = "Overview"
    INCOME_NAME = "Income Statement"
    CASH_NAME = "Cash Flow Statement"
    VALUATION_NAME = "Valuation"
    START_BAL_NAME = "Starting Balance Sheet"
    ENDING_BAL_NAME = "Ending Balance Sheet"

    def __init__(self, parent=None, period=None):
        self.id = ID()  # does not get its own bbid, just holds namespace

        # parent for Financials is BusinessUnit
        self.relationships = Relationships(self, parent=parent)

        self._period = period
        self._restricted = False
        self._full_order = [self.OVERVIEW_NAME, self.INCOME_NAME,
                            self.CASH_NAME, self.START_BAL_NAME, 
                            self.ENDING_BAL_NAME, self.VALUATION_NAME]

        statements = [Statement(name=self.OVERVIEW_NAME, parent=self, 
                                period=period),
                      Statement(name=self.INCOME_NAME, parent=self, 
                                period=period),
                      CashFlow(name=self.CASH_NAME, parent=self, 
                               period=period),
                      Statement(name=self.VALUATION_NAME, parent=self, 
                                period=period, compute=False),
                      BalanceSheet(name=self.START_BAL_NAME, parent=self, 
                                   period=period),
                      BalanceSheet(name=self.ENDING_BAL_NAME, parent=self, 
                                   period=period)]

        self._statement_directory = dict()
        for stmt in statements:
            self._statement_directory[stmt.name.casefold()] = stmt

        self.update_statements = list()

    @property
    def overview(self):
        return self.get_statement(self.OVERVIEW_NAME)

    @overview.setter
    def overview(self, value):
        self._statement_directory[self.OVERVIEW_NAME.casefold()] = value

    @property
    def income(self):
        return self.get_statement(self.INCOME_NAME)

    @income.setter
    def income(self, value):
        self._statement_directory[self.INCOME_NAME.casefold()] = value

    @property
    def cash(self):
        return self.get_statement(self.CASH_NAME)

    @cash.setter
    def cash(self, value):
        self._statement_directory[self.CASH_NAME.casefold()] = value

    @property
    def valuation(self):
        return self.get_statement(self.VALUATION_NAME)

    @valuation.setter
    def valuation(self, value):
        self._statement_directory[self.VALUATION_NAME.casefold()] = value

    @property
    def starting(self):
        return self.get_statement(self.START_BAL_NAME)

    @starting.setter
    def starting(self, value):
        self._statement_directory[self.START_BAL_NAME.casefold()] = value

    @property
    def ending(self):
        return self.get_statement(self.ENDING_BAL_NAME)

    @ending.setter
    def ending(self, value):
        self._statement_directory[self.ENDING_BAL_NAME.casefold()] = value

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
        for name in self._full_order:
            statement = self.get_statement(name)
            result.append(statement)

        return result

    @property
    def has_valuation(self):
        return not self.valuation == Statement(self.VALUATION_NAME)

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value
        for statement in self._statement_directory.values():
            if statement:
                if statement.relationships.parent is self:
                    statement.set_period(value)

    def __str__(self):
        header = ''

        period = self.period #or self.relationships.parent.period
        if period:
            if Equalities.multi_getattr(self, "relationships.parent", None):
                header = (
                    '{begin:^{width}}\n\n'
                    '{start:^{width}}\n'
                    '{close:^{width}}\n\n'
                ).format(
                    width=bb_settings.SCREEN_WIDTH,
                    begin='Financial statements for {}'.format(
                        self.relationships.parent.tags.name
                    ),
                    start='Period starting: {}'.format(period.start),
                    close='Period ending:   {}'.format(period.end),
                )

        content = []
        for statement in self.full_ordered:
            if statement is not None:
                content.append(str(statement))

        result = (
            '{header}'
            '{content}\n'
            '{border:^{width}}\n\n'
        ).format(
            width=bb_settings.SCREEN_WIDTH,
            header=header,
            content=''.join(content),
            border="***",
        )

        return result

    @classmethod
    def from_database(cls, portal_data, company, **kargs):
        """

        Financials.from_database(portal_data) -> Financials

        **CLASS METHOD**

        Method extracts Financials from portal_data.
        """
        period = kargs['period']
        new = cls(parent=company, period=period)
        new.register(company.id.bbid)

        us = portal_data['update_statements']
        new.update_statements = us

        # new._chef_order = portal_data['chef_order']
        # new._compute_order = portal_data['compute_order']
        # new._exclude_statements = portal_data['exclude_statements']
        new._full_order = portal_data['full_order']

        for data in portal_data['statements']:
            statement = Statement.from_database(
                data, financials=new
            )
            new._statement_directory[statement.name.casefold()] = statement

        return new

    def to_database(self):
        """

        Financials.to_database() -> dict

        Method yields a serialized representation of self.
        """
        self.check_balance_sheets()

        statements = []
        for name in self._full_order:
            statement = self.get_statement(name)
            if statement:
                data = statement.to_database()
                data['attr_name'] = name
                statements.append(data)

        result = {
            'statements': statements,
            # 'chef_order': self._chef_order,
            # 'compute_order': self._compute_order,
            # 'exclude_statements': self._exclude_statements,
            'full_order': self._full_order,
            'update_statements': self.update_statements,
        }
        return result

    def add_statement(self, name, statement=None, title=None, position=None,
                      compute=True, overwrite=False):
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
        if name.casefold() in self._statement_directory and not overwrite:
            c = "%s already exists as a statement!" % name
            raise bb_exceptions.BlackbirdError(c)

        if not self._restricted:
            if not statement:
                use_name = title or name
                statement = Statement(use_name, period=self.period,
                                      compute=compute)

            statement.relationships.set_parent(self)

            self._statement_directory[name.casefold()] = statement

            if position:
                self._full_order.insert(position, name)
            else:
                self._full_order.append(name)

            if self.id.namespace:
                statement.register(self.id.namespace)

    def build_tables(self):
        """


        Financials.build_tables() -> None


        Build tables for each defined statement.
        """
        self.run_on_all("build_tables")

    def check_balance_sheets(self):
        start_lines = self.starting.get_full_ordered()
        start_names = [line.name for line in start_lines]

        end_lines = self.ending.get_full_ordered()
        end_names = [line.name for line in end_lines]

        if start_names != end_names:
            # only run the increments if there is a mismatch
            self.starting.increment(self.ending, consolidating=False,
                                    over_time=True)
            self.ending.increment(self.starting, consolidating=False,
                                  over_time=True)

    def copy(self, clean=False):
        """


        Financials.copy() -> Financials


        Return a deep copy of instance.

        Method starts with a shallow copy and then substitutes deep copies
        for the values of each attribute in instance.ORDER
        """
        new_instance = Financials()
        new_instance._full_order = self._full_order.copy()

        for key, stmt in self._statement_directory.items():
            new_statement = stmt.copy(clean=clean)
            new_statement.relationships.set_parent(new_instance)
            new_instance._statement_directory[key] = new_statement

        new_instance.id = ID()
        new_instance.register(self.id.namespace)

        return new_instance

    def find_line(self, line_id, statement_attr):
        """


        Financials.find_line() -> LineItem

        --``line_id`` bbid of line

        Finds a LineItem across all statements by its bbid.
        """
        if isinstance(line_id, str):
            line_id = ID.from_database(line_id).bbid

        statement = self.get_statement(statement_attr)
        if statement:
            for line in statement.get_full_ordered():
                if line.id.bbid == line_id:
                    return line

        raise bb_exceptions.StructureError(
            'Could not find line with id {}'.format(line_id)
        )

    def get_covenant_statements(self):
        """


        Financials.get_covenant_statements() -> list

        Method compiles list of covenant statements tied to instance, returned
        in order dictated by _full_order.
        """
        result = list()
        for stmt in self.full_ordered:
            if stmt.type == stmt.COVENANT_TYPE:
                result.append(stmt)

        return result

    def get_kpi_statements(self):
        """


        Financials.get_kpi_statements() -> list

        Method compiles list of kpi statements tied to instance, returned
        in order dictated by _full_order.
        """
        result = list()
        for stmt in self.full_ordered:
            if stmt.type == stmt.KPI_TYPE:
                result.append(stmt)

        return result

    def get_regular_statements(self):
        """


        Financials.get_regular_statements() -> list

        Method compiles list of regular statements tied to instance, returned
        in order dictated by _full_order.
        """
        result = list()
        for stmt in self.full_ordered:
            if stmt.type == stmt.REGULAR_TYPE:
                result.append(stmt)

        return result

    def get_statement(self, name):

        if isinstance(name, str):
            name = name.casefold()
            if name in self._statement_directory:
                return self._statement_directory[name]
            else:
                outs = list()
                for k in self._statement_directory.keys():
                    if name in k:
                        outs.append(self._statement_directory[k])

                if len(outs) == 1:
                    return outs[0]
                elif len(outs) > 1:
                    c = "Statement with exact name not found. " \
                        "Multiple statements with partial matching" \
                        " name were found."
                    raise KeyError(c)

        return None

    def peer_locator(self):
        """


        Financials.peer_locator() -> Financials

        Given a parent container from another time period, return a function
        locating a copy of ourselves within that container.
        """

        def locator(bu, **kargs):
            peer = bu.get_financials(kargs['period'])
            return peer
        return locator

    def populate_from_stored_values(self, period):
        """


        Financials.populate_from_stored_values() -> None

        --``period`` is the TimePeriod from which to retrieve values

        Method uses financials data (values and excel info) stored in the
        period to fill in the line values in the instance.
        """
        tl = period.relationships.parent
        if len(tl.keys()) > 0:
            min_dt = min(tl.keys())
            first = tl[min_dt]
        else:
            first = None

        for statement in self.full_ordered:
            if statement is not None and (statement is not self.starting or period is first):
                for line in statement.get_full_ordered():
                    line.xl_data = LineData(line)

                    if not line._details or not line.sum_details:
                        value = period.get_line_value(line.id.bbid.hex)
                        line._local_value = value

                    hc = period.get_line_hc(line.id.bbid.hex)
                    line._hardcoded = hc

        buid = self.relationships.parent.id.bbid
        past = period.past
        future = period.future

        # Now check if fins exist in period.past
        if past:
            if buid in past.financials:
                # past financials already exist as rich objects,
                # so we can just link to existing ending balance sheet
                past_fins = past.financials[buid]
                self.starting = past_fins.ending
            else:
                # past financials have not yet been re-inflated, so we have to
                # make an Ending Balance Sheet and pretend it belongs to the
                # preceding period
                self.starting = self.ending.copy()
                self.starting.set_period(past)

                for line in self.starting.get_full_ordered():
                    line.xl_data = LineData(line)

                    if not line._details or not line.sum_details:
                        value = past.get_line_value(line.id.bbid.hex)
                        line._local_value = value

                    hc = past.get_line_hc(line.id.bbid.hex)
                    line._hardcoded = hc

        # And if fins exist in period.future
        if future:
            if buid in future.financials:
                future_fins = future.financials[buid]
                future_fins.starting = self.ending

    def register(self, namespace):
        """


        Financials.register() -> None

        --``namespace`` is the namespace to assign to instance

        Method sets namespace of instance, does not assign an actual ID.
        Registers statements on instance.
        """
        self.id.set_namespace(namespace)

        for statement in self._statement_directory.values():
            if statement:
                statement.register(self.id.namespace)

    def reset(self):
        """


        StatementBundle.reset() -> None


        Reset each defined statement.
        """
        self.run_on_all("reset")

    def restrict(self):
        self._restricted = True
        for statement in self._statement_directory.values():
            if statement is not None:
                statement.restrict()

    def run_on_all(self, action, *kargs, **pargs):
        """


        Bundle.run_on_all() -> None


        Run ``statement.action(*kargs, **pargs)`` for all defined statements
        in instance.ordered.

        Expects ``action`` to be a string naming the statement method.
        """
        for statement in self.full_ordered:
            if statement:
                if statement.compute and statement is not self.starting:
                    routine = getattr(statement, action)
                    routine(*kargs, **pargs)

    def summarize(self):
        """


        StatementBundle.summarize() -> None


        Summarize each defined statement.
        """
        self.run_on_all("summarize")
