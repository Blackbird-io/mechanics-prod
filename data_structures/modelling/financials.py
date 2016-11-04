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

from collections import OrderedDict

import bb_settings

from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from .statement import Statement
from .line_item import LineItem
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
        self.overview = Statement(name="overview", parent=self)
        self.income = Statement(name="income statement", parent=self)
        self.cash = CashFlow(parent=self)
        self.valuation = Statement("Valuation", parent=self)
        self.starting = BalanceSheet("Starting Balance Sheet", parent=self)
        self.ending = BalanceSheet("Ending Balance Sheet", parent=self)
        self.ledger = None
        self.id = ID()  # does not get its own bbid, just holds namespace
        self.relationships = Relationships(self, parent=parent)
        self.period = period
        self.filled = False

        # defaults for monthly; quarterly and annual need to overwrite
        self.complete = True
        self.periods_used = 1

        self._full_order = [
            "overview", "income", "cash", "starting", "ending",
            "ledger", "valuation"
        ]
        self._chef_order = [
            "overview", "income", "cash", "starting", "ending", "ownership"
        ]
        self._compute_order = ['overview', 'income', 'cash']
        self._exclude_statements = ['valuation', 'starting']

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

    @classmethod
    def from_portal(cls, period, portal_data):
        """


        Financials.from_portal(portal_model) -> Model

        **CLASS METHOD**

        Method extracts a Financials from serialized representation.
        """
        # a data structure to convert flat list to a nested dict
        tree_nodes = OrderedDict()
        # Pass one: create data structures for tree representation
        # every parent-child relationship is at the top level but also hold
        # all the nested relationships
        # buid -> statement attribute name -> line id
        for line in portal_data:
            buid_node = tree_nodes.setdefault(line['buid'], {})
            attr_node = buid_node.setdefault(line['statement_attr'], {})
            line_node = attr_node.setdefault(line['line_id'], dict(
                myself = line,
                parent = line['line_parent_id'],
                subset = OrderedDict(),
            ))
        # Pass two: nest child lines within parents. Top-level nodes that don't
        # have a parent are the root nodes of the tree.
        for buid, buid_node in tree_nodes.items():
            for attr, attr_node in buid_node.items():
                for id, node in attr_node.items():
                    if node['parent']:
                        attr_node[node['parent']]['subset'][id] = node
        financials_set = {}
        for buid, buid_node in tree_nodes.items():
            for attr, attr_node in buid_node.items():
                for id, node in attr_node.items():
                    # restrict operation to root nodes
                    if not node['parent']:
                        line = node['myself']
                        if buid not in financials_set:
                            fins = cls(period=period)
                            financials_set[buid] = fins
                        fins = financials_set[buid]
                        if not hasattr(fins, attr):
                            statement = Statement(
                                line['statement_name'], parent=fins
                            )
                            setattr(fins, attr, statement)
                        statement = getattr(fins, attr)
                        LineItem.from_portal(statement, node)

        return financials_set

    def to_portal(self, period, buid):
        """


        Model.to_portal(portal_model) -> Model


        Method extracts a TimeLine from ``portal_data``.

        Method expects ``portal_data`` to be a dict.
        """
        for statement_attr in self._full_order:
            statement = getattr(self, statement_attr, None)
            if statement:
                for line_index, line in enumerate(statement.get_ordered()):
                    # line is yielded first, followed by _details
                    yield from line.to_portal(
                        period, buid, statement, statement_attr, line_index
                    )

    def __str__(self):
        period =  self.period or self.relationships.parent.period
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
        else:
            header = ''

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

        if not statement:
            use_name = title or name
            statement = Statement(use_name)

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

    def copy(self):
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
        for name in self.full_order:
            own_statement = getattr(self, name)
            if own_statement is not None:
                new_statement = own_statement.copy()
                new_statement.relationships.set_parent(new_instance)
                setattr(new_instance, name, new_statement)

        new_instance.id = ID()
        new_instance.register(self.id.namespace)
        return new_instance

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
        self.filled = False

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
