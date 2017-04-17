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
    ====================  ======================================================
    """

    def __init__(self, parent=None, period=None):
        self.overview = Statement(name="overview", parent=self, period=period)
        self.income = Statement(name="income statement", parent=self,
                                period=period)
        self.cash = CashFlow(parent=self, period=period)
        self.valuation = Statement("Valuation", parent=self, period=period)
        self.starting = BalanceSheet("Starting Balance Sheet", parent=self, period=period)
        self.ending = BalanceSheet("Ending Balance Sheet", parent=self, period=period)
        self.ledger = None
        self.id = ID()  # does not get its own bbid, just holds namespace

        # parent for Financials is BusinessUnit
        self.relationships = Relationships(self, parent=parent)

        self._period = period
        # self.filled = False

        # defaults for monthly; quarterly and annual need to overwrite
        # self.complete = True
        # self.periods_used = 1

        self._full_order = [
            "overview", "income", "cash", "starting", "ending",
            "ledger", "valuation"
        ]
        self._chef_order = [
            "overview", "income", "cash", "starting", "ending"
        ]
        self._compute_order = ['overview', 'income', 'cash']
        self._exclude_statements = ['valuation', 'starting']

        self._restricted = False

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

        for name in self._full_order:
            statement = getattr(self, name)
            result.append(statement)

        return result

    @property
    def has_valuation(self):
        return not self.valuation == Statement("Valuation")

    @property
    def order(self):
        order = self.full_order
        for name in self._exclude_statements:
            order.remove(name)

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

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value
        for statement in self.full_ordered:
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
    def from_portal(cls, portal_data, company, **kargs):
        """

        Financials.from_portal(portal_data) -> Financials

        **CLASS METHOD**

        Method extracts Financials from portal_data.
        """
        period = kargs['period']
        new = cls(parent=company, period=period)
        new.register(company.id.bbid)

        for attr in ('_chef_order',
                     '_compute_order',
                     '_exclude_statements',
                     '_full_order'):
            new.__dict__[attr] = portal_data[attr]

        for data in portal_data['statements']:
            attr_name = data['name']

            statement = Statement.from_portal(
                data, financials=new
            )

            new.__dict__[attr_name] = statement

        return new

    def to_portal(self):
        """

        Financials.to_portal() -> dict

        Method yields a serialized representation of self.
        """
        self.check_balance_sheets()

        statements = []
        for name in self._full_order:
            if name == 'starting' and self.period:
                if self.period.past is not None:
                    # enforce SSOT in database
                    continue

            statement = getattr(self, name, None)
            if statement:
                data = statement.to_portal()
                data.update({'name': name})
                statements.append(data)

        result = {
            'statements': statements,
            '_chef_order': self._chef_order,
            '_compute_order': self._compute_order,
            '_exclude_statements': self._exclude_statements,
            '_full_order': self._full_order,
        }
        return result

    def chef_ordered(self):
        """

        Financials.chef_ordered() -> iter(Statement)

        Method yields own statements in order displayed on a spreadsheet.
        """

        for name in self._chef_order:
            yield name, getattr(self, name, None)

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
        if not self._restricted:
            if not statement:
                use_name = title or name
                statement = Statement(use_name, period=self.period)

            statement.relationships.set_parent(self)

            self.__dict__[name] = statement

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
                self._chef_order.append(name)
            else:
                self._exclude_statements.append(name)

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
        new_instance._compute_order = self._compute_order.copy()
        new_instance._exclude_statements = self._exclude_statements.copy()
        new_instance._chef_order = self._chef_order.copy()
        for name in self.full_order:
            own_statement = getattr(self, name)
            if own_statement is not None:
                new_statement = own_statement.copy(clean=clean)
                new_statement.relationships.set_parent(new_instance)

                new_instance.__dict__[name] = new_statement

        new_instance.id = ID()
        new_instance.register(self.id.namespace)

        return new_instance

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
                    new_xl = LineData()
                    new_xl.format = line.xl.format
                    line.xl = new_xl

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
                    new_xl = LineData()
                    new_xl.format = line.xl.format  # for posterity, and for
                    line.xl = new_xl

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

        for statement in self.full_ordered:
            if statement:
                statement.register(self.id.namespace)

    def reset(self):
        """


        StatementBundle.reset() -> None


        Reset each defined statement.
        """
        self.run_on_all("reset")
        # self.filled = False

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

    def find_line(self, line_id, statement_attr):
        """


        Financials.find_line() -> LineItem

        --``line_id`` bbid of line

        Finds a LineItem across all statements by its bbid.
        """
        if isinstance(line_id, str):
            line_id = ID.from_portal(line_id).bbid

        statement = getattr(self, statement_attr, None)
        if statement:
            for line in statement.get_full_ordered():
                if line.id.bbid == line_id:
                    return line

        raise bb_exceptions.StructureError(
            'Could not find line with id {}'.format(line_id)
        )

    def restrict(self):
        self._restricted = True
        for statement in self.full_ordered:
            if statement is not None:
                statement.restrict()
